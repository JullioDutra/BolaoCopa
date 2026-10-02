import json

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required
from futebol.escudos import escudo_url

from . import copa, dados, engine, servico
from .models import DraftCopa7a0, Partida7a0, Temporada7a0


def _card(time):
    return {**time, 'escudo': escudo_url(time['clube']) or ''}


def _times_cards():
    return [_card(t) for t in dados.todos()]


@acesso_liberado_required
def hub(request):
    partidas = Partida7a0.objects.filter(usuario=request.user)
    abertas = partidas.exclude(status='fim').exclude(modo__in=['temporada', 'copa'])[:3]
    drafts = DraftCopa7a0.objects.filter(usuario=request.user, status__in=['montando', 'copa'])
    temporadas = Temporada7a0.objects.filter(usuario=request.user, status='andamento')
    recentes = partidas.filter(status='fim').exclude(modo='copa')[:5]
    copas = DraftCopa7a0.objects.filter(usuario=request.user).exclude(status__in=['montando', 'copa'])[:4]
    return render(request, 'setezero/hub.html', {
        'abertas': abertas, 'drafts': drafts, 'copas': copas, 'temporadas': temporadas, 'recentes': recentes,
        'dados': dados, 'total_times': len(dados.TIMES),
        'jogos': partidas.filter(status='fim').count(),
        'melhor_saldo': max([p.saldo for p in partidas.filter(status='fim').exclude(modo='copa')], default=0),
        'nomes': {k: dados.obter(k)['nome'] for k in dados.TIMES} | {k: dados.obter(k)['nome'] for k in dados.FREGUESES},
    })


@acesso_liberado_required
def novo(request, modo):
    if modo not in ('amistoso', 'desafio', 'temporada'):
        return redirect('setezero:hub')
    if request.method == 'POST':
        try:
            if modo == 'temporada':
                temporada = servico.criar_temporada(request.user, request.POST.get('time'))
                return redirect('setezero:temporada', pk=temporada.pk)
            partida = servico.criar_partida(
                request.user, modo, request.POST.get('time'), request.POST.get('rival') or None,
                formacao=request.POST.get('formacao'), mentalidade=request.POST.get('mentalidade', 'equilibrado'),
                estilo=request.POST.get('estilo', 'posse'))
            return redirect('setezero:partida', pk=partida.pk)
        except servico.ErroJogo as e:
            messages.error(request, str(e))
    return render(request, 'setezero/novo.html', {
        'modo': modo, 'times': _times_cards(), 'formacoes': list(dados.FORMACOES),
        'mentalidades': engine.MENTALIDADES, 'estilos': engine.ESTILOS,
        'fregueses': [_card(t) for t in dados.fregueses()] if modo == 'desafio' else [],
    })


@acesso_liberado_required
def partida(request, pk):
    p = get_object_or_404(Partida7a0, pk=pk, usuario=request.user)
    return render(request, 'setezero/partida.html', {
        'partida': p, 'mentalidades': engine.MENTALIDADES, 'estilos': engine.ESTILOS,
    })


def _json_corpo(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


@acesso_liberado_required
def api_estado(request, pk):
    p = get_object_or_404(Partida7a0, pk=pk, usuario=request.user)
    try:
        desde = int(request.GET.get('desde', 0))
    except ValueError:
        desde = 0
    return JsonResponse({'visao': servico.visao(p), 'eventos': p.estado['eventos'][desde:], 'desde': desde})


@acesso_liberado_required
@require_POST
def api_avancar(request, pk):
    """ Joga alguns minutos. Corpo: {"ate": "intervalo"|"fim"|N, "maximo": minutos, "desde": índice, "ajuste": {...}} """
    p = get_object_or_404(Partida7a0, pk=pk, usuario=request.user)
    corpo = _json_corpo(request)
    try:
        if corpo.get('ajuste'):
            servico.ajustar(p, corpo['ajuste'])
        desde = int(corpo.get('desde', len(p.estado['eventos'])))
        try:
            maximo = max(1, min(45, int(corpo['maximo']))) if corpo.get('maximo') else None
        except (TypeError, ValueError):
            maximo = None
        if corpo.get('ate'):
            servico.avancar(p, corpo['ate'], maximo)
            p.refresh_from_db()
    except servico.ErroJogo as e:
        return JsonResponse({'erro': str(e)}, status=400)
    return JsonResponse({'visao': servico.visao(p), 'eventos': p.estado['eventos'][desde:]})


@acesso_liberado_required
@require_POST
def api_simular(request, pk):
    """ O usuário abre mão de comandar: a partida é jogada inteira pelas IAs. """
    p = get_object_or_404(Partida7a0, pk=pk, usuario=request.user)
    while p.status != 'fim':
        servico.avancar(p, 'fim')
        p.refresh_from_db()
    return JsonResponse({'visao': servico.visao(p), 'eventos': p.estado['eventos']})


@acesso_liberado_required
def temporada(request, pk):
    t = get_object_or_404(Temporada7a0, pk=pk, usuario=request.user)
    jogo = servico.jogo_do_usuario(t)
    e = t.estado
    rodada_atual = e['rodada']
    proximo = None
    if jogo:
        casa, fora, lado = jogo
        proximo = {'casa': _card(dados.obter(casa)), 'fora': _card(dados.obter(fora)), 'lado': lado}
    meus = [r for r in e['resultados'] if t.time_usuario in (r['casa'], r['fora'])]
    for r in meus:
        r['casa_nome'], r['fora_nome'] = dados.obter(r['casa'])['nome'], dados.obter(r['fora'])['nome']
    linhas = servico.tabela_ordenada(t)
    for l in linhas:
        l['escudo'] = escudo_url(l['time']['clube']) or ''
    return render(request, 'setezero/temporada.html', {
        't': t, 'tabela': linhas, 'proximo': proximo, 'rodada': rodada_atual + 1, 'total_rodadas': len(e['calendario']),
        'meus': meus[::-1][:6], 'meu_time': _card(dados.obter(t.time_usuario)),
    })


@acesso_liberado_required
@require_POST
def temporada_jogar(request, pk):
    t = get_object_or_404(Temporada7a0, pk=pk, usuario=request.user)
    partida = servico.partida_da_rodada(t)
    if partida is None:
        return redirect('setezero:temporada', pk=t.pk)
    return redirect('setezero:partida', pk=partida.pk)


@acesso_liberado_required
def ranking(request):
    dados_rank = servico.ranking()
    for p in dados_rank['goleadas']:
        p.meu_nome = dados.obter(p.time_usuario)['nome']
        p.rival_nome = dados.obter(p.time_rival)['nome']
    return render(request, 'setezero/ranking.html', dados_rank)


# ------------------------------------------------------------------ Draft Copa do Brasil

def _brief(time):
    """ Time sorteado pronto para o front: elenco agrupado por posição. """
    return {'chave': time['chave'], 'nome': time['nome'], 'clube': time['clube'], 'ano': time['ano'], 'apelido': time.get('apelido', ''),
            'cor': time['cor'], 'escudo': escudo_url(time['clube']) or '', 'overall': time['overall'],
            'elenco': sorted(time['elenco'], key=lambda j: (['GOL', 'ZAG', 'LAT', 'VOL', 'MEI', 'PON', 'ATA'].index(j['pos']), -j['nota']))}


def _visao_draft(d):
    e = d.estado
    pend = dados.obter(e['pendente']) if e['pendente'] else None
    return {'status': d.status, 'formacao': d.formacao, 'slots': e['slots'], 'banco': e['banco'],
            'posicoes': copa.posicoes_slots(d), 'skips': e['skips'], 'pendente': _brief(pend) if pend else None,
            'completo': copa.completo(d), 'escolhidos': sum(1 for j in e['slots'] + e['banco'] if j)}


@acesso_liberado_required
def draft_novo(request):
    if request.method == 'POST':
        d = copa.criar_draft(request.user, request.POST.get('formacao', '4-3-3'), request.POST.get('mentalidade', 'equilibrado'))
        return redirect('setezero:draft', pk=d.pk)
    return render(request, 'setezero/draft_novo.html', {
        'formacoes': list(dados.FORMACOES), 'mentalidades': engine.MENTALIDADES, 'total_times': len(dados.TIMES), 'fases': copa.FASES})


@acesso_liberado_required
def draft(request, pk):
    d = get_object_or_404(DraftCopa7a0, pk=pk, usuario=request.user)
    if d.status in ('campeao', 'eliminado', 'terminou'):
        return redirect('setezero:retrospecto', codigo=d.codigo)
    if d.status == 'copa':
        return render(request, 'setezero/copa.html', _contexto_copa(d))
    return render(request, 'setezero/draft.html', {'d': d, 'visao': _visao_draft(d), 'fases': copa.FASES, 'banco_total': copa.BANCO})


def _contexto_copa(d):
    fases = []
    for i, nome in enumerate(copa.FASES):
        feito = d.campanha[i] if i < len(d.campanha) else None
        rival = dados.obter(d.estado['rivais'][i])
        fases.append({'nome': nome, 'feito': feito, 'atual': i == d.fase, 'rival': {**rival, 'escudo': escudo_url(rival['clube']) or ''}})
    meu = copa.time_do_draft(d)
    return {'d': d, 'fases': fases, 'meu': meu, 'titulares': d.estado['slots'], 'banco': d.estado['banco']}


def _json(request):
    try:
        return json.loads(request.body or '{}')
    except ValueError:
        return {}


@acesso_liberado_required
@require_POST
def api_draft(request, pk, acao):
    d = get_object_or_404(DraftCopa7a0, pk=pk, usuario=request.user)
    corpo = _json(request)
    try:
        if acao == 'sortear':
            copa.sortear(d)
        elif acao == 'pular':
            copa.pular(d)
        elif acao == 'escolher':
            copa.escolher(d, corpo.get('nome'), corpo.get('destino'))
        elif acao == 'iniciar':
            copa.iniciar_copa(d)
        else:
            return JsonResponse({'erro': 'Ação inválida.'}, status=400)
    except copa.ErroDraft as e:
        return JsonResponse({'erro': str(e), 'visao': _visao_draft(d)}, status=400)
    d.refresh_from_db()
    return JsonResponse({'visao': _visao_draft(d), 'status': d.status})


@acesso_liberado_required
@require_POST
def draft_jogar(request, pk):
    d = get_object_or_404(DraftCopa7a0, pk=pk, usuario=request.user)
    p = copa.partida_da_fase(d)
    if p is None:
        return redirect('setezero:draft', pk=d.pk)
    return redirect('setezero:partida', pk=p.pk)


def retrospecto(request, codigo):
    """ Página pública (por link secreto) para compartilhar no grupo. """
    d = get_object_or_404(DraftCopa7a0, codigo=codigo)
    if d.status in ('montando', 'copa'):
        if request.user.is_authenticated and d.usuario_id == request.user.id:
            return redirect('setezero:draft', pk=d.pk)
        raise Http404
    r = copa.retrospecto(d)
    url = request.build_absolute_uri()
    t = r['titulo']
    texto = (f"🏆 {t['manchete'].title()} no 7 a 0 da Cartolândia! {r['vitorias']}V {r['derrotas']}D, "
             f"{r['gols_pro']} gols marcados. Duvido você fazer melhor 👉 {url}")
    r.update(url=url, texto_whats=texto, meu=request.user.is_authenticated and d.usuario_id == request.user.id)
    return render(request, 'setezero/retrospecto.html', r)

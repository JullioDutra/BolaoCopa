import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required
from futebol.escudos import escudo_url

from . import dados, engine, servico
from .models import Partida7a0, Temporada7a0


def _card(time):
    return {**time, 'escudo': escudo_url(time['clube']) or ''}


def _times_cards():
    return [_card(t) for t in dados.todos()]


@acesso_liberado_required
def hub(request):
    partidas = Partida7a0.objects.filter(usuario=request.user)
    abertas = partidas.exclude(status='fim').exclude(modo='temporada')[:3]
    temporadas = Temporada7a0.objects.filter(usuario=request.user, status='andamento')
    recentes = partidas.filter(status='fim')[:5]
    return render(request, 'setezero/hub.html', {
        'abertas': abertas, 'temporadas': temporadas, 'recentes': recentes,
        'dados': dados, 'total_times': len(dados.TIMES),
        'jogos': partidas.filter(status='fim').count(),
        'melhor_saldo': max([p.saldo for p in partidas.filter(status='fim')], default=0),
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
        'voltar': ('setezero:temporada', p.temporada_id) if p.temporada_id else ('setezero:hub', None),
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

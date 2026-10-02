from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required
from palpites import api_futebol
from palpites.models import Jogo

from . import comparativo as regras
from . import scout as scouting
from . import servico
from .models import Atleta, Comparativo, Time
from .posicoes import NOME_POSICAO, ORDEM_POSICAO


def _times_com_elenco():
    return Time.objects.annotate(n=Count('atletas')).filter(n__gt=0).order_by('nome')


@acesso_liberado_required
def hub(request):
    return render(request, 'futebol/hub.html', {
        'total_times': Time.objects.count(), 'total_atletas': Atleta.objects.count(),
        'comparativos': Comparativo.objects.select_related('time_a', 'time_b').filter(encerrado=False)[:6],
    })


@acesso_liberado_required
def buscar(request):
    q = (request.GET.get('q') or '').strip()
    resultado = servico.buscar(q, limite=30)
    return render(request, 'futebol/busca.html', {'q': q, **resultado})


@acesso_liberado_required
def api_buscar(request):
    """ Autocomplete: JSON enxuto com até 6 times e 6 jogadores. """
    r = servico.buscar(request.GET.get('q', ''), limite=6)
    return JsonResponse({
        'times': [{'id': t.id, 'nome': t.nome, 'sub': t.liga or t.pais, 'escudo': t.escudo_src or '',
                   'url': reverse('futebol:time', args=[t.id])} for t in r['times']],
        'jogadores': [{'id': a.id, 'nome': a.nome, 'sub': f"{a.get_posicao_display()} · {a.time.nome if a.time else 'sem time'}",
                       'url': reverse('futebol:jogador', args=[a.id])} for a in r['jogadores']],
    })


@acesso_liberado_required
def time_detalhe(request, pk):
    time = get_object_or_404(Time.objects.select_related('clube_local'), pk=pk)
    atletas = sorted(time.atletas.all(), key=lambda a: (ORDEM_POSICAO.get(a.posicao, 9), a.numero or 99, a.nome))
    grupos = [{'posicao': p, 'nome': NOME_POSICAO[p], 'atletas': [a for a in atletas if a.posicao == p]}
              for p in ('GOL', 'DEF', 'MEI', 'ATA')]
    temporadas = scouting.temporadas_disponiveis()
    return render(request, 'futebol/time.html', {
        'balanco': scouting.balanco_time(time, temporadas[0]) if temporadas else None,
        'time': time, 'grupos': [g for g in grupos if g['atletas']], 'total': len(atletas),
        'forma': servico.forma_local(time.nome),
        'proximos': Jogo.objects.filter(finalizado=False, data_hora__gte=timezone.now())
                    .filter(Q(time_casa=time.nome) | Q(time_fora=time.nome)).order_by('data_hora')[:4],
    })


@acesso_liberado_required
def jogador_detalhe(request, pk):
    atleta = get_object_or_404(Atleta.objects.select_related('time'), pk=pk)
    colegas = atleta.time.atletas.exclude(pk=atleta.pk).filter(posicao=atleta.posicao)[:6] if atleta.time else []
    avaliacoes = [scouting.avaliar(e) for e in atleta.estatisticas.select_related('time')]
    return render(request, 'futebol/jogador.html', {'atleta': atleta, 'colegas': colegas, 'avaliacoes': avaliacoes})


@acesso_liberado_required
def scout(request):
    """ Mitou ou bagre? Rankings de rendimento por temporada, posição e contratações. """
    temporadas = scouting.temporadas_disponiveis()
    try:
        temporada = int(request.GET.get('temporada') or (temporadas[0] if temporadas else 0)) or None
    except ValueError:
        temporada = None
    posicao = request.GET.get('posicao') if request.GET.get('posicao') in NOME_POSICAO else ''
    so_contratados = request.GET.get('contratados') == '1'
    dados = scouting.ranking(temporada, posicao=posicao, contratados=so_contratados)
    times = [t for t in Time.objects.filter(estatisticas__temporada=temporada).distinct()] if temporada else []
    balancos = [(t, scouting.balanco_time(t, temporada)) for t in times]
    balancos = sorted([b for b in balancos if b[1]], key=lambda b: -b[1]['media'])
    return render(request, 'futebol/scout.html', {
        'temporadas': temporadas, 'temporada': temporada, 'posicao': posicao, 'contratados': so_contratados,
        'posicoes': NOME_POSICAO.items(), 'dados': dados, 'balancos': balancos,
    })


@acesso_liberado_required
def tabela(request):
    try:
        linhas = api_futebol.classificacao()
    except api_futebol.ApiIndisponivel:
        linhas = []
    return render(request, 'futebol/tabela.html', {'linhas': linhas})


@acesso_liberado_required
def artilharia(request):
    return render(request, 'futebol/artilharia.html', {'artilheiros': servico.artilharia(limite=20)})


@acesso_liberado_required
def api_ao_vivo(request):
    return JsonResponse({'jogos': servico.ao_vivo()})


@acesso_liberado_required
def api_noticias(request):
    return JsonResponse({'noticias': servico.noticias_gerais()})


@acesso_liberado_required
def api_raio_x(request, jogo_id):
    jogo = get_object_or_404(Jogo, pk=jogo_id)
    return JsonResponse(servico.raio_x(jogo))


# ------------------------------------------------------------ comparar times + votação dos 11

def _pega_time(valor):
    try:
        return Time.objects.filter(pk=int(valor)).first()
    except (TypeError, ValueError):
        return None


@acesso_liberado_required
def comparar(request):
    a, b = _pega_time(request.GET.get('a')), _pega_time(request.GET.get('b'))
    comparacao = servico.comparar_times(a, b) if a and b else None
    return render(request, 'futebol/comparar.html', {
        'times': _times_com_elenco(), 'a': a, 'b': b, 'comparacao': comparacao,
        'forma_a': servico.forma_local(a.nome) if a else [], 'forma_b': servico.forma_local(b.nome) if b else [],
        'h2h': servico.confronto_local(a.nome, b.nome) if a and b else [],
    })


def _agrupar(atletas, marcados):
    grupos = []
    for pos in ('GOL', 'DEF', 'MEI', 'ATA'):
        lista = sorted((x for x in atletas if x.posicao == pos), key=lambda x: (-(x.overall or 0), x.numero or 99, x.nome))
        grupos.append({'posicao': pos, 'nome': NOME_POSICAO[pos], 'atletas': [(x, x.id in marcados) for x in lista]})
    return grupos


@acesso_liberado_required
def comparativo_novo(request):
    a, b = _pega_time(request.GET.get('a') or request.POST.get('a')), _pega_time(request.GET.get('b') or request.POST.get('b'))
    if not a or not b:
        messages.info(request, "Escolha os dois times primeiro.")
        return redirect('futebol:comparar')

    if request.method == 'POST':
        try:
            encerra = request.POST.get('encerra_em') or None
            encerra_em = None
            if encerra:
                from datetime import datetime
                encerra_em = timezone.make_aware(datetime.strptime(encerra, '%Y-%m-%dT%H:%M'))
            comp = regras.criar(request.user, a, b, request.POST.getlist('lado_a'), request.POST.getlist('lado_b'),
                                request.POST.get('titulo', ''), encerra_em)
        except (regras.ComparativoInvalido, ValueError) as erro:
            messages.error(request, str(erro) or "Dados inválidos.")
        else:
            messages.success(request, "Votação aberta! Agora chama a galera pra eleger os 11 melhores.")
            return redirect('futebol:comparativo', pk=comp.pk)

    sel_a = {x.id for x in regras.sugerir_titulares(a)}
    sel_b = {x.id for x in regras.sugerir_titulares(b)}
    if request.method == 'POST':
        sel_a, sel_b = {int(i) for i in request.POST.getlist('lado_a') if i.isdigit()}, {int(i) for i in request.POST.getlist('lado_b') if i.isdigit()}
    return render(request, 'futebol/comparativo_novo.html', {
        'a': a, 'b': b, 'grupos_a': _agrupar(list(a.atletas.all()), sel_a), 'grupos_b': _agrupar(list(b.atletas.all()), sel_b),
    })


@acesso_liberado_required
def comparativo_lista(request):
    return render(request, 'futebol/comparativo_lista.html', {
        'comparativos': Comparativo.objects.select_related('time_a', 'time_b', 'criador').annotate(votantes=Count('votos__usuario', distinct=True))[:40],
    })


@acesso_liberado_required
def comparativo_detalhe(request, pk):
    comp = get_object_or_404(Comparativo.objects.select_related('time_a', 'time_b', 'criador'), pk=pk)
    meus = regras.meus_votos(request.user, comp)
    ap = regras.apuracao(comp)
    itens = regras.candidatos(comp)
    grupos = {'A': [], 'B': []}
    for e in itens:
        grupos[e.lado].append((e.atleta, e.atleta_id in meus))
    return render(request, 'futebol/comparativo.html', {
        'comp': comp, 'ap': ap, 'grupos_a': grupos['A'], 'grupos_b': grupos['B'], 'ja_votou': bool(meus),
        'formacao': regras.FORMACAO, 'recompensa': regras.RECOMPENSA_VOTO,
        'pode_encerrar': request.user == comp.criador or request.user.is_staff,
        'url_compartilhar': request.build_absolute_uri(reverse('futebol:comparativo', args=[comp.pk])),
    })


@acesso_liberado_required
@require_POST
def comparativo_votar(request, pk):
    comp = get_object_or_404(Comparativo, pk=pk)
    try:
        primeira = regras.votar(request.user, comp, [i for i in request.POST.getlist('atleta') if i.isdigit()])
        messages.success(request, "Voto registrado!" + (f" +{regras.RECOMPENSA_VOTO} Cartola Coins." if primeira else " (você pode mudar até a votação fechar)"))
    except regras.ComparativoInvalido as erro:
        messages.error(request, str(erro))
    return redirect('futebol:comparativo', pk=pk)


@acesso_liberado_required
@require_POST
def comparativo_encerrar(request, pk):
    comp = get_object_or_404(Comparativo, pk=pk)
    if request.user != comp.criador and not request.user.is_staff:
        raise Http404()
    comp.encerrado = True
    comp.save(update_fields=['encerrado'])
    messages.success(request, "Votação encerrada. Aí está o 11 eleito!")
    return redirect('futebol:comparativo', pk=pk)

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required

from . import engine, historicos, servico
from .models import PartidaArbitro


@acesso_liberado_required
def hub(request):
    partidas = PartidaArbitro.objects.filter(usuario=request.user)
    return render(request, 'arbitro/hub.html', {
        'aberta': partidas.filter(status='andamento').first(),
        'recentes': partidas.filter(status='fim')[:6],
        'numeros': servico.numeros_usuario(request.user),
        'categorias': engine.CATEGORIAS.values(),
        'total_historicos': len(historicos.todos()),
        'lances_por_partida': engine.LANCES_POR_PARTIDA,
        'premio_max': engine.premio(engine.LANCES_POR_PARTIDA),
    })


@acesso_liberado_required
@require_POST
def nova(request):
    partida = servico.criar_partida(request.user)
    return redirect('arbitro:partida', pk=partida.pk)


@acesso_liberado_required
def partida(request, pk):
    p = get_object_or_404(PartidaArbitro, pk=pk, usuario=request.user)
    if p.status == 'fim':
        return redirect('arbitro:resultado', pk=p.pk)
    return render(request, 'arbitro/partida.html', {'partida': p})


@acesso_liberado_required
def resultado(request, pk):
    p = get_object_or_404(PartidaArbitro, pk=pk, usuario=request.user)
    if p.status != 'fim':
        return redirect('arbitro:partida', pk=p.pk)
    return render(request, 'arbitro/resultado.html', {
        'partida': p, 'resumo': servico.resumo(p), 'sumula': servico.sumula(p),
    })


@acesso_liberado_required
def ranking(request):
    return render(request, 'arbitro/ranking.html', servico.ranking())


# --- APIs (JSON) ---
def _json(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return {}


@acesso_liberado_required
def api_lance(request, pk):
    p = get_object_or_404(PartidaArbitro, pk=pk, usuario=request.user)
    return JsonResponse(servico.lance_atual(p))


@acesso_liberado_required
@require_POST
def api_var(request, pk):
    get_object_or_404(PartidaArbitro, pk=pk, usuario=request.user)
    try:
        return JsonResponse({'ok': True, 'var': servico.chamar_var(pk, request.user)})
    except servico.ErroJogo as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=400)


@acesso_liberado_required
@require_POST
def api_responder(request, pk):
    get_object_or_404(PartidaArbitro, pk=pk, usuario=request.user)
    dados = _json(request)
    try:
        indice = int(dados.get('indice', -1))
    except (TypeError, ValueError):
        indice = -1
    try:
        return JsonResponse({'ok': True, **servico.responder(pk, request.user, indice, dados.get('resposta'))})
    except servico.ErroJogo as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=400)

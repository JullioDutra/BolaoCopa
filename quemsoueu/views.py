import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required

from . import engine, servico
from .craques import CRAQUES
from .models import PartidaQSE


@acesso_liberado_required
def hub(request):
    hoje = timezone.localdate()
    return render(request, 'quemsoueu/hub.html', {
        'do_dia': PartidaQSE.objects.filter(usuario=request.user, modo='diario', dia=hoje).first(),
        'ranking_dia': servico.ranking_do_dia(hoje), 'ranking_geral': servico.ranking_geral(),
        'numeros': servico.numeros(request.user), 'total_craques': len(CRAQUES),
        'max_perguntas': engine.MAX_PERGUNTAS, 'max_palpites': engine.MAX_PALPITES,
    })


@acesso_liberado_required
def desafio(request):
    return redirect('quemsoueu:rodada', pk=servico.desafio_do_dia(request.user).pk)


@acesso_liberado_required
@require_POST
def treino(request):
    return redirect('quemsoueu:rodada', pk=servico.novo_treino(request.user).pk)


@acesso_liberado_required
def rodada(request, pk):
    p = get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return render(request, 'quemsoueu/rodada.html', {
        'partida': p, 'rapidas': [(r[0], r[1]) for r in engine.RAPIDAS], 'max_perguntas': engine.MAX_PERGUNTAS,
    })


# --- APIs (JSON) ---
def _json(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return {}


def _executar(acao):
    try:
        return JsonResponse({'ok': True, **acao()})
    except servico.ErroJogo as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=400)


@acesso_liberado_required
def api_estado(request, pk):
    p = get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return JsonResponse({'ok': True, **servico.estado(p, request.user)})


@acesso_liberado_required
@require_POST
def api_rapida(request, pk):
    get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return _executar(lambda: servico.perguntar_rapida(pk, request.user, _json(request).get('id')))


@acesso_liberado_required
@require_POST
def api_perguntar(request, pk):
    get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return _executar(lambda: servico.perguntar_ia(pk, request.user, _json(request).get('texto')))


@acesso_liberado_required
@require_POST
def api_dica(request, pk):
    get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return _executar(lambda: servico.pedir_dica(pk, request.user))


@acesso_liberado_required
@require_POST
def api_palpite(request, pk):
    get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return _executar(lambda: servico.palpitar(pk, request.user, _json(request).get('palpite')))


@acesso_liberado_required
@require_POST
def api_desistir(request, pk):
    get_object_or_404(PartidaQSE, pk=pk, usuario=request.user)
    return _executar(lambda: servico.desistir(pk, request.user))

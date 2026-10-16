import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required

from . import servico
from .fases import FASES


@acesso_liberado_required
def hub(request):
    numeros = servico.numeros(request.user)
    return render(request, 'cabecudos/hub.html', {
        'fases': [{**f, 'n': i + 1, 'liberada': i + 1 <= numeros['liberada']} for i, f in enumerate(FASES)],
        'numeros': numeros, 'ranking': servico.ranking(),
    })


@acesso_liberado_required
def jogar(request, fase):
    if not 1 <= fase <= servico.fase_liberada(request.user):
        return redirect('cabecudos:hub')
    return render(request, 'cabecudos/jogar.html', {'fase': fase, 'rival': FASES[fase - 1], 'total_fases': len(FASES)})


def _json(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return {}


@acesso_liberado_required
@require_POST
def api_iniciar(request):
    try:
        _, config = servico.iniciar(request.user, _json(request).get('fase'))
        return JsonResponse({'ok': True, **config})
    except servico.ErroJogo as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=400)


@acesso_liberado_required
@require_POST
def api_finalizar(request):
    d = _json(request)
    try:
        return JsonResponse({'ok': True, **servico.finalizar(request.user, d.get('token'), d.get('gols_pro'), d.get('gols_contra'))})
    except servico.ErroJogo as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=400)

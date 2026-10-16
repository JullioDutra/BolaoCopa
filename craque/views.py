import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from bolao.decorators import acesso_liberado_required

from . import servico
from .dados import CLUBES, CLUBES_INICIAIS, POSICOES, MAX_TEMPORADAS
from .models import Carreira


@acesso_liberado_required
def hub(request):
    return render(request, 'craque/hub.html', {
        'ativa': servico.ativa(request.user),
        'encerradas': Carreira.objects.filter(usuario=request.user, status='encerrada')[:5],
        'hall': servico.hall_da_fama(),
        'clubes': [(n, CLUBES[n][0], CLUBES[n][1]) for n in CLUBES_INICIAIS], 'posicoes': list(POSICOES),
        'max_temporadas': MAX_TEMPORADAS,
    })


@acesso_liberado_required
@require_POST
def nova(request):
    try:
        c = servico.criar(request.user, request.POST.get('nome'), request.POST.get('posicao'),
                          request.POST.get('clube'), request.POST.get('numero'))
    except servico.ErroJogo as e:
        messages.error(request, str(e))
        return redirect('craque:hub')
    return redirect('craque:carreira', pk=c.pk)


@acesso_liberado_required
def carreira(request, pk):
    c = get_object_or_404(Carreira, pk=pk, usuario=request.user)
    return render(request, 'craque/carreira.html', {'c': c})


# --- APIs (JSON) ---
def _json(request):
    try:
        return json.loads(request.body or b'{}')
    except ValueError:
        return {}


def _responder(acao):
    try:
        return JsonResponse({'ok': True, **servico.visao(acao())})
    except servico.ErroJogo as e:
        return JsonResponse({'ok': False, 'erro': str(e)}, status=400)


@acesso_liberado_required
def api_estado(request, pk):
    c = servico.recuperar(get_object_or_404(Carreira, pk=pk, usuario=request.user))
    return JsonResponse({'ok': True, **servico.visao(c)})


@acesso_liberado_required
@require_POST
def api_decidir(request, pk):
    get_object_or_404(Carreira, pk=pk, usuario=request.user)
    return _responder(lambda: servico.decidir(pk, request.user, _json(request).get('opcao')))


@acesso_liberado_required
@require_POST
def api_coletiva(request, pk):
    get_object_or_404(Carreira, pk=pk, usuario=request.user)
    d = _json(request)
    return _responder(lambda: servico.responder_coletiva(pk, request.user, d.get('texto'), d.get('pronta')))


@acesso_liberado_required
@require_POST
def api_seguir(request, pk):
    get_object_or_404(Carreira, pk=pk, usuario=request.user)
    return _responder(lambda: servico.seguir(pk, request.user, _json(request).get('clube') or None))

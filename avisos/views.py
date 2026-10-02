import json
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import PerfilUsuario
from palpites.models import Jogo, Palpite
from palpites.ranking_utils import calcular_ranking_geral

from . import servico, whatsapp
from .models import Notificacao, PushSubscription


def sw_js(request):
    """ Service Worker servido na RAIZ (escopo "/"), exigência para push funcionar no site inteiro. """
    arquivo = Path(settings.BASE_DIR) / 'static_files' / 'sw.js'
    resposta = HttpResponse(arquivo.read_text(encoding='utf-8'), content_type='application/javascript')
    resposta['Service-Worker-Allowed'] = '/'
    resposta['Cache-Control'] = 'no-cache'
    return resposta


@login_required
def api_chave(request):
    return JsonResponse({'chave': getattr(settings, 'VAPID_PUBLIC_KEY', None) or '', 'ativo': servico.vapid_configurado()})


@login_required
@require_POST
def api_inscrever(request):
    try:
        dados = json.loads(request.body)
        endpoint, chaves = dados['endpoint'], dados['keys']
        p256dh, auth = chaves['p256dh'], chaves['auth']
    except (ValueError, KeyError, TypeError):
        return JsonResponse({'ok': False}, status=400)
    if not str(endpoint).startswith('https://'):
        return JsonResponse({'ok': False}, status=400)
    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={'usuario': request.user, 'p256dh': p256dh, 'auth': auth,
                  'aparelho': (request.META.get('HTTP_USER_AGENT') or '')[:120]},
    )
    return JsonResponse({'ok': True})


@login_required
@require_POST
def api_cancelar(request):
    try:
        endpoint = json.loads(request.body).get('endpoint')
    except ValueError:
        endpoint = None
    PushSubscription.objects.filter(usuario=request.user, endpoint=endpoint).delete()
    return JsonResponse({'ok': True})


@login_required
@require_POST
def testar(request):
    aviso = servico.notificar(request.user, "🔔 Teste de notificação", "Tudo certo! Você vai receber os avisos da Cartolândia aqui.",
                              url=reverse('avisos:central'), tipo='teste')
    ok = PushSubscription.objects.filter(usuario=request.user, ultimo_envio_ok__isnull=False).exists()
    messages.success(request, "Teste enviado! Se ativou o push, ele chega no aparelho em instantes." if ok or servico.vapid_configurado()
                     else "Aviso criado na sua caixa de entrada (o push ainda não está configurado no servidor).")
    return redirect('avisos:central')


@login_required
def central(request):
    """ Caixa de entrada: lista os avisos e marca todos como lidos ao abrir. """
    avisos = list(Notificacao.objects.filter(usuario=request.user)[:60])
    Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)
    return render(request, 'avisos/central.html', {
        'avisos': avisos,
        'push_ativo': servico.vapid_configurado(),
        'aparelhos': PushSubscription.objects.filter(usuario=request.user).count(),
        'grupo_url': whatsapp.link_grupo(),
    })


# ------------------------------------------------------------------ staff

def _jogos_sem_palpite():
    """ [(jogo, [usuários sem palpite])] para os próximos jogos que ainda aceitam palpite. """
    agora = timezone.now()
    ativos = User.objects.filter(is_active=True)
    saida = []
    for jogo in Jogo.objects.filter(finalizado=False, data_hora__gt=agora).order_by('data_hora')[:6]:
        if not jogo.aceita_palpite:
            continue
        com = set(Palpite.objects.filter(jogo=jogo).values_list('usuario_id', flat=True))
        saida.append((jogo, [u for u in ativos if u.id not in com]))
    return saida


@staff_member_required
def staff_painel(request):
    """ Painel da staff: avisar a galera (push + caixa) e chamar no WhatsApp. """
    if request.method == 'POST':
        titulo = (request.POST.get('titulo') or '').strip()
        texto = (request.POST.get('texto') or '').strip()
        url = (request.POST.get('url') or '/').strip()
        if not titulo:
            messages.error(request, "Escreva um título para o aviso.")
        else:
            if not url.startswith('/'):
                url = '/'
            n = servico.notificar_varios(User.objects.filter(is_active=True), titulo, texto, url, tipo='staff')
            messages.success(request, f"Aviso enviado para {n} pessoa(s).")
        return redirect('avisos:staff')

    perfis = {p.usuario_id: p for p in PerfilUsuario.objects.all()}
    pendencias = []
    for jogo, usuarios in _jogos_sem_palpite():
        cobrar = []
        for u in usuarios:
            p = perfis.get(u.id)
            if p and p.telefone and p.avisos_whatsapp:
                texto = (f"Fala, {u.first_name or 'craque'}! Falta você palpitar em {jogo.time_casa} x {jogo.time_fora} "
                         f"({jogo.data_hora.astimezone().strftime('%d/%m %H:%M')}). Bora? {request.build_absolute_uri('/palpites/jogos/')}")
                cobrar.append({'usuario': u, 'link': whatsapp.link_chat(p.telefone, texto)})
        pendencias.append({'jogo': jogo, 'total': len(usuarios), 'cobrar': cobrar})

    resumo = whatsapp.texto_resumo(
        calcular_ranking_geral(), list(Jogo.objects.filter(finalizado=False, data_hora__gt=timezone.now()).order_by('data_hora')[:5]),
        request.build_absolute_uri('/'))
    return render(request, 'avisos/staff.html', {
        'pendencias': pendencias, 'resumo': resumo, 'link_resumo': whatsapp.link_compartilhar(resumo),
        'push_ativo': servico.vapid_configurado(),
        'inscritos_push': PushSubscription.objects.values('usuario').distinct().count(),
        'total_usuarios': User.objects.filter(is_active=True).count(),
    })



@login_required
def resenha(request):
    """ Feed completo "Resenha ao vivo". """
    from .atividade import icone
    from .models import Atividade
    itens = [{'a': a, 'icone': icone(a.tipo)} for a in Atividade.objects.select_related('usuario')[:80]]
    return render(request, 'avisos/resenha.html', {'itens': itens})

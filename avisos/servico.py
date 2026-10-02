"""
Envio de avisos: caixa de entrada no site + Web Push (celular/PWA).

Web Push precisa de chaves VAPID (gere com `python manage.py gerar_vapid` e ponha no .env) e do pacote
`pywebpush`. Sem isso o aviso continua aparecendo na caixa de entrada do site — nada quebra.
"""
import json
import logging

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Notificacao, PushSubscription

logger = logging.getLogger(__name__)


def vapid_configurado():
    return bool(getattr(settings, 'VAPID_PUBLIC_KEY', None) and getattr(settings, 'VAPID_PRIVATE_KEY', None))


def _webpush():
    try:
        from pywebpush import WebPushException, webpush
        return webpush, WebPushException
    except ImportError:
        return None, None


def enviar_push(sub, payload):
    """ Envia a um aparelho. Devolve True/False; remove assinaturas mortas (404/410). """
    webpush, WebPushException = _webpush()
    if webpush is None or not vapid_configurado():
        return False
    try:
        webpush(
            subscription_info={'endpoint': sub.endpoint, 'keys': {'p256dh': sub.p256dh, 'auth': sub.auth}},
            data=json.dumps(payload),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={'sub': getattr(settings, 'VAPID_EMAIL', 'mailto:contato@cartolandia.app')},
            ttl=60 * 60 * 12,
        )
    except WebPushException as erro:
        status = getattr(getattr(erro, 'response', None), 'status_code', None)
        if status in (404, 410):
            sub.delete()
        else:
            logger.warning("Falha no push para %s: %s", sub.usuario_id, erro)
        return False
    except Exception as erro:                                  # rede, chave inválida, etc.
        logger.warning("Erro inesperado no push: %s", erro)
        return False
    PushSubscription.objects.filter(pk=sub.pk).update(ultimo_envio_ok=timezone.now())
    return True


def notificar(usuario, titulo, texto='', url='/', tipo='geral', chave='', push=True):
    """
    Cria o aviso na caixa de entrada e tenta o push. Com `chave` repetida para o mesmo usuário
    nada é criado (idempotente) e devolve None. Devolve a Notificacao criada.
    """
    try:
        with transaction.atomic():
            aviso = Notificacao.objects.create(usuario=usuario, titulo=titulo[:120], texto=texto[:300],
                                               url=url or '/', tipo=tipo, chave=chave)
    except IntegrityError:
        return None
    if push:
        payload = {'titulo': aviso.titulo, 'texto': aviso.texto, 'url': aviso.url, 'tag': chave or f'aviso-{aviso.pk}'}
        for sub in PushSubscription.objects.filter(usuario=usuario):
            enviar_push(sub, payload)
    return aviso


def notificar_varios(usuarios, titulo, texto='', url='/', tipo='geral', chave=''):
    return sum(1 for u in usuarios if notificar(u, titulo, texto, url, tipo, chave))

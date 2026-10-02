"""Auditoria da staff reaproveitando o LogEntry do Django (sem tabela nova, aparece também no /admin/)."""
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

PREFIXO = '[gestão] '


def registrar(request, mensagem, alvo=None):
    alvo = alvo or request.user
    LogEntry.objects.create(
        user_id=request.user.pk,
        content_type_id=ContentType.objects.get_for_model(User).pk,
        object_id=str(alvo.pk),
        object_repr=str(alvo)[:200],
        action_flag=CHANGE,
        change_message=PREFIXO + mensagem,
    )


def recentes(limite=100):
    return (LogEntry.objects.filter(change_message__startswith=PREFIXO)
            .select_related('user').order_by('-action_time')[:limite])

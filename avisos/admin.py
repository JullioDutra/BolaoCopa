from django.contrib import admin

from .models import Notificacao, PushSubscription


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'aparelho', 'criada_em', 'ultimo_envio_ok')
    search_fields = ('usuario__username', 'usuario__first_name')


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'titulo', 'tipo', 'lida', 'criada_em')
    list_filter = ('tipo', 'lida')
    search_fields = ('usuario__username', 'titulo')

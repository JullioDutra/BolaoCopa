from django.contrib import admin

from .models import Carreira


@admin.register(Carreira)
class CarreiraAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'usuario', 'status', 'pontuacao', 'premio_total', 'atualizado_em')
    list_filter = ('status',)
    search_fields = ('usuario__username',)
    readonly_fields = ('estado', 'pendente', 'historico')

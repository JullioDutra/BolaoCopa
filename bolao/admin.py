from django.contrib import admin
from .models import Participacao

@admin.register(Participacao)
class ParticipacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'aprovado', 'data_adesao')
    list_filter = ('tipo', 'aprovado')
    search_fields = ('usuario__username',)
    list_editable = ('aprovado',) # Permite aprovar o Pix direto na lista!
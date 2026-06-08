from django.contrib import admin
# Importe os models do Draft se já não estiverem importados
from .models import ClubeBrasileiro, ElencoHistorico, JogadorDraft, SessaoDraft, EscolhaDraft

@admin.register(ClubeBrasileiro)
class ClubeBrasileiroAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(ElencoHistorico)
class ElencoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('clube', 'ano', 'forca_base')
    list_filter = ('clube', 'ano')

@admin.register(JogadorDraft)
class JogadorDraftAdmin(admin.ModelAdmin):
    list_display = ('nome', 'posicao', 'nota_geral', 'elenco')
    list_filter = ('posicao', 'elenco__clube')
    search_fields = ('nome', 'elenco__clube__nome')

@admin.register(SessaoDraft)
class SessaoDraftAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'formacao', 'status', 'fase_atual', 'data_inicio')
    list_filter = ('status', 'formacao')
from django.contrib import admin
from .models import CategoriaDesafio, ItemDesafio, PartidaDuelo, Clube, JogadorBanco

# --- NOVOS BANCOS CENTRALIZADOS ---
@admin.register(Clube)
class ClubeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tem_escudo')
    search_fields = ('nome',)
    
    def tem_escudo(self, obj):
        return bool(obj.escudo)
    tem_escudo.short_description = 'Escudo Inserido?'
    tem_escudo.boolean = True

@admin.register(JogadorBanco)
class JogadorBancoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

# --- DESAFIOS E PARTIDAS ---
class ItemDesafioInline(admin.TabularInline):
    model = ItemDesafio
    extra = 1
    # Adicionamos os novos campos de busca nativos do Django Admin para facilitar a sua vida!
    autocomplete_fields = ['clube_vinculado', 'jogador_vinculado'] 

@admin.register(CategoriaDesafio)
class CategoriaDesafioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'resposta_oculta')
    list_filter = ('tipo',)
    search_fields = ('titulo',)
    inlines = [ItemDesafioInline]

@admin.register(PartidaDuelo)
class PartidaDueloAdmin(admin.ModelAdmin):
    list_display = ('jogador_criador', 'jogador_convidado', 'categoria', 'status', 'vencedor')
    list_filter = ('status',)
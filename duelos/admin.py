from django.contrib import admin
from .models import CategoriaDesafio, ItemDesafio, PartidaDuelo

class ItemDesafioInline(admin.TabularInline):
    model = ItemDesafio
    extra = 1

@admin.register(CategoriaDesafio)
class CategoriaDesafioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo')
    inlines = [ItemDesafioInline] # Permite cadastrar os jogadores/escudos na mesma tela da categoria!

@admin.register(PartidaDuelo)
class PartidaDueloAdmin(admin.ModelAdmin):
    list_display = ('jogador_criador', 'jogador_convidado', 'categoria', 'status', 'turno_de')
from django.contrib import admin
from .models import Jogador, Convocacao

@admin.register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'posicao', 'clube_atual')
    search_fields = ('nome', 'clube_atual')
    list_filter = ('posicao',)

@admin.register(Convocacao)
class ConvocacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'total_convocados', 'data_atualizacao')
    search_fields = ('usuario__username',)
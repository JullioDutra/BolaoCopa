from django.contrib import admin
from .models import Jogo, Palpite

@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    # 1. ADICIONAMOS OS GOLS AQUI NO list_display (para eles aparecerem na tela)
    list_display = ('time_casa', 'gols_casa_real', 'gols_fora_real', 'time_fora', 'data_hora', 'finalizado')
    
    list_filter = ('finalizado', 'data_hora')
    
    # 2. Agora o Django permite que eles sejam editáveis!
    list_editable = ('gols_casa_real', 'gols_fora_real', 'finalizado') 

@admin.register(Palpite)
class PalpiteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'jogo', 'gols_casa', 'gols_fora', 'pontuacao_obtida')
    search_fields = ('usuario__username', 'jogo__time_casa')
    list_filter = ('jogo',)
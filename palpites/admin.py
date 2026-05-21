from django.contrib import admin
from .models import Jogo, Palpite, OscarCartolandia

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

@admin.register(OscarCartolandia)
class OscarCartolandiaAdmin(admin.ModelAdmin):
    # O que vai aparecer nas colunas da tabela principal
    list_display = ('autor', 'categoria_formatada', 'nivel', 'indicado_por', 'data_criacao')
    
    # Filtros laterais para facilitar a vida do tribunal
    list_filter = ('categoria', 'nivel', 'data_criacao')
    
    # Barra de pesquisa (busca pelo nome do autor, na fala ou pelo usuário que indicou)
    search_fields = ('autor', 'fala', 'indicado_por__username', 'indicado_por__first_name')
    
    # Impede que a data de criação seja editada sem querer
    readonly_fields = ('data_criacao',)
    
    # Organiza por data, do mais recente para o mais antigo
    ordering = ('-data_criacao',)

    # Deixa o nome da categoria mais bonito na tabela do Admin
    @admin.display(description='Categoria')
    def categoria_formatada(self, obj):
        return obj.get_categoria_display()

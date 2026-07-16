from django.contrib import admin
from .models import Jogo, Palpite, OscarCartolandia
from django.contrib import admin
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import Jogo, Palpite, OscarCartolandia, Clube, Temporada, PalpiteLongoPrazo, MuralCampeoes

from convocacao.models import Convocacao

# ==========================================
# ACTION: FINALIZAR TEMPORADA E GERAR MURAL
# ==========================================
@admin.action(description='🏁 Finalizar Temporada Atual e Gerar Mural de Campeões')
def finalizar_temporada(modeladmin, request, queryset):
    for temporada in queryset:
        if not temporada.ativa:
            modeladmin.message_user(request, f"A temporada {temporada.ano} já está encerrada.", level='WARNING')
            continue

        usuarios = User.objects.all()
        campeao = None
        maior_pontuacao = -1

        for user in usuarios:
            # 1. Busca os pontos dos Jogos Normais do Bolão
            pontos_jogos = Palpite.objects.filter(usuario=user).aggregate(total=Sum('pontuacao_obtida'))['total'] or 0
            
            # 2. Busca os pontos dos Palpites de Longo Prazo (G4, Z4, Campeões)
            pontos_longo = PalpiteLongoPrazo.objects.filter(usuario=user, temporada=temporada).aggregate(total=Sum('pontos_obtidos'))['total'] or 0
            
            # 3. Busca os pontos da Seleção do Brasileirão / Copa
            pontos_selecao = Convocacao.objects.filter(usuario=user).aggregate(total=Sum('pontuacao_total'))['total'] or 0

            # SOMA GERAL PARA O RANKING
            pontuacao_total_usuario = pontos_jogos + pontos_longo + pontos_selecao

            # Verifica se é o maior pontuador até agora
            if pontuacao_total_usuario > maior_pontuacao:
                maior_pontuacao = pontuacao_total_usuario
                campeao = user

        # Salva o grande campeão no Mural
        if campeao:
            MuralCampeoes.objects.create(
                temporada=temporada,
                usuario=campeao,
                pontuacao_final=maior_pontuacao
            )

        # Encerra a temporada atual
        temporada.ativa = False
        temporada.save()

        # Inicia a próxima temporada automaticamente
        Temporada.objects.get_or_create(ano=temporada.ano + 1, defaults={'ativa': True})

        # =========================================================
        # ZERANDO O BOLÃO PARA COMEÇAR DO ZERO (Descomente se quiser)
        # =========================================================
        # Como você disse que quer "começá-la do zero novamente":
        # Descomente as linhas abaixo se quiser deletar os palpites e jogos antigos.
        # Palpite.objects.all().delete()
        # Jogo.objects.all().delete()
        # Convocacao.objects.all().delete()

        modeladmin.message_user(request, f"Temporada {temporada.ano} encerrada com sucesso! O Campeão foi {campeao.username} com {maior_pontuacao} pontos! 🏆")


# ==========================================
# REGISTRO DOS ADMINS E MODELOS
# ==========================================

class TemporadaAdmin(admin.ModelAdmin):
    list_display = ('ano', 'ativa')
    list_filter = ('ativa',)
    actions = [finalizar_temporada] # Acopla o botão na tela de Temporadas

class PalpiteLongoPrazoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'clube', 'posicao_esperada', 'pontos_obtidos', 'temporada')
    list_filter = ('tipo', 'temporada')
    search_fields = ('usuario__username', 'clube__nome')

class MuralCampeoesAdmin(admin.ModelAdmin):
    list_display = ('temporada', 'usuario', 'pontuacao_final', 'data_conquista')

# Registrando os novos modelos para você poder gerenciá-los no painel
admin.site.register(Temporada, TemporadaAdmin)
admin.site.register(PalpiteLongoPrazo, PalpiteLongoPrazoAdmin)
admin.site.register(MuralCampeoes, MuralCampeoesAdmin)
admin.site.register(Clube)

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

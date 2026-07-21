from django.contrib import admin
from .models import Jogo, Palpite, OscarCartolandia, Clube, Temporada, PalpiteLongoPrazo, MuralCampeoes
from .ranking_utils import calcular_ranking_geral

from convocacao.models import SelecaoBrasileirao


# ==========================================
# ACTION: FINALIZAR TEMPORADA E GERAR MURAL
# ==========================================
@admin.action(description='🏁 Finalizar Temporada Atual e Gerar Mural de Campeões (zera o ciclo)')
def finalizar_temporada(modeladmin, request, queryset):
    for temporada in queryset:
        if not temporada.ativa:
            modeladmin.message_user(request, f"A temporada {temporada.ano} já está encerrada.", level='WARNING')
            continue

        # Usa a MESMA regra de pontuação da tela de Ranking Geral, então o
        # campeão do Mural é sempre exatamente quem estava em 1º lugar no ranking.
        ranking = calcular_ranking_geral(temporada=temporada)

        if ranking:
            primeiro = ranking[0]
            MuralCampeoes.objects.create(
                temporada=temporada,
                usuario=primeiro['usuario'],
                pontuacao_final=primeiro['total_pontos']
            )
            campeao_nome = primeiro['usuario'].username
            campeao_pontos = primeiro['total_pontos']
        else:
            campeao_nome = "ninguém (sem palpites na temporada)"
            campeao_pontos = 0

        # Encerra a temporada atual e abre a próxima
        temporada.ativa = False
        temporada.save()
        Temporada.objects.get_or_create(ano=temporada.ano + 1, defaults={'ativa': True})

        # =========================================================
        # ZERANDO O BOLÃO PARA COMEÇAR DO ZERO
        # Descomente as linhas abaixo se quiser realmente resetar os dados.
        # =========================================================
        # Palpite.objects.all().delete()
        # Jogo.objects.all().delete()
        # PalpiteLongoPrazo.objects.filter(temporada=temporada).delete()
        # SelecaoBrasileirao.objects.update(pontuacao_total=0)

        modeladmin.message_user(
            request,
            f"Temporada {temporada.ano} encerrada com sucesso! O Campeão foi {campeao_nome} com {campeao_pontos} pontos! 🏆"
        )


@admin.action(description='🔄 Recalcular pontuação das Seleções 4-3-3 do Brasileirão')
def recalcular_selecoes_brasileirao(modeladmin, request, queryset):
    for selecao in queryset:
        selecao.calcular_pontuacao()
    modeladmin.message_user(request, "Pontuações recalculadas com base nos jogadores oficiais marcados.")


# ==========================================
# REGISTRO DOS ADMINS E MODELOS
# ==========================================

class TemporadaAdmin(admin.ModelAdmin):
    list_display = ('ano', 'ativa')
    list_filter = ('ativa',)
    actions = [finalizar_temporada]


class PalpiteLongoPrazoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'clube', 'posicao_esperada', 'pontos_obtidos', 'temporada')
    list_filter = ('tipo', 'temporada')
    search_fields = ('usuario__username', 'clube__nome')


class MuralCampeoesAdmin(admin.ModelAdmin):
    list_display = ('temporada', 'usuario', 'pontuacao_final', 'data_conquista')


class ClubeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cor_hexadecimal', 'escudo')


admin.site.register(Temporada, TemporadaAdmin)
admin.site.register(PalpiteLongoPrazo, PalpiteLongoPrazoAdmin)
admin.site.register(MuralCampeoes, MuralCampeoesAdmin)
admin.site.register(Clube, ClubeAdmin)


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ('time_casa', 'gols_casa_real', 'gols_fora_real', 'time_fora', 'data_hora', 'finalizado')
    list_filter = ('finalizado', 'data_hora')
    list_editable = ('gols_casa_real', 'gols_fora_real', 'finalizado')


@admin.register(Palpite)
class PalpiteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'jogo', 'gols_casa', 'gols_fora', 'pontuacao_obtida')
    search_fields = ('usuario__username', 'jogo__time_casa')
    list_filter = ('jogo',)


@admin.register(OscarCartolandia)
class OscarCartolandiaAdmin(admin.ModelAdmin):
    list_display = ('autor', 'categoria_formatada', 'nivel', 'indicado_por', 'data_criacao')
    list_filter = ('categoria', 'nivel', 'data_criacao')
    search_fields = ('autor', 'fala', 'indicado_por__username', 'indicado_por__first_name')
    readonly_fields = ('data_criacao',)
    ordering = ('-data_criacao',)

    @admin.display(description='Categoria')
    def categoria_formatada(self, obj):
        return obj.get_categoria_display()


@admin.register(SelecaoBrasileirao)
class SelecaoBrasileiraoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pontuacao_total', 'data_atualizacao')
    actions = [recalcular_selecoes_brasileirao]

admin.site.register(Clube)
admin.site.register(TorneioLongoPrazo)
admin.site.register(PalpiteTorneioExtra)

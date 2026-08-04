from django.contrib import admin
from django.utils.html import format_html
from .models import EstatisticaJogador, RankingMinijogo


@admin.register(EstatisticaJogador)
class EstatisticaJogadorAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'nome', 'clube', 'posicao', 'gols', 'assistencias', 'cartoes', 'ativo')
    list_editable = ('ativo',)
    list_filter = ('posicao', 'ativo', 'clube')
    search_fields = ('nome', 'clube')

    def miniatura(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:40px;height:40px;object-fit:cover;border-radius:50%;" />',
                obj.foto.url,
            )
        return "—"
    miniatura.short_description = "Foto"


@admin.register(RankingMinijogo)
class RankingMinijogoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'pontuacao', 'maior_sequencia', 'data_partida')
    list_filter = ('data_partida',)
    search_fields = ('usuario__username',)
    ordering = ('-pontuacao',)

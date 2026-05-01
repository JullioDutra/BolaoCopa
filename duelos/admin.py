from django.contrib import admin
from .models import (
    CategoriaDesafio, 
    ItemDesafio, 
    PartidaDuelo, 
    Clube, 
    JogadorBanco, 
    Campeonato, 
    InscricaoCampeonato, 
    ConfrontoCampeonato,
    # Nossos modelos novos do Mini Fanáticos:
    ClubeFutebol, 
    PerguntaClube, 
    PartidaMiniFanaticos, 
    JogadorMiniFanaticos
)

# ==========================================
# BANCOS CENTRALIZADOS (X1 RAIZ)
# ==========================================
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

# ==========================================
# DESAFIOS E PARTIDAS (X1 RAIZ)
# ==========================================
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
    # Voltei pro padrão antigo (sem as fugas), já que o anti-doping tá na geladeira por enquanto
    list_display = ('jogador_criador', 'jogador_convidado', 'categoria', 'status', 'vencedor')
    list_filter = ('status',)
    
    # NOVA LINHA: Resolve o erro E040 ensinando o Django a pesquisar partidas
    search_fields = ('id', 'jogador_criador__username', 'jogador_convidado__username')

# ==========================================
# MODO CAMPEONATO
# ==========================================
@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'admin', 'status', 'data_limite_inscricao', 'criado_em')
    list_filter = ('status', 'criado_em')
    search_fields = ('nome', 'admin__username', 'admin__first_name')
    readonly_fields = ('codigo_convite', 'criado_em')
    list_editable = ('status',) # Permite mudar o status direto na listagem

@admin.register(InscricaoCampeonato)
class InscricaoCampeonatoAdmin(admin.ModelAdmin):
    list_display = ('jogador', 'campeonato', 'data_inscricao')
    list_filter = ('campeonato', 'data_inscricao')
    search_fields = ('jogador__username', 'jogador__first_name', 'campeonato__nome')

@admin.register(ConfrontoCampeonato)
class ConfrontoCampeonatoAdmin(admin.ModelAdmin):
    list_display = ('campeonato', 'fase', 'ordem_chave', 'jogador1', 'jogador2', 'status', 'vencedor')
    list_filter = ('campeonato', 'fase', 'status')
    search_fields = ('jogador1__username', 'jogador2__username', 'campeonato__nome')
    autocomplete_fields = ('jogador1', 'jogador2', 'vencedor', 'desafio_sorteado', 'partida_vinculada')

# ==========================================
# MODO MINI FANÁTICOS (2v2)
# ==========================================
@admin.register(ClubeFutebol)
class ClubeFutebolAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(PerguntaClube)
class PerguntaClubeAdmin(admin.ModelAdmin):
    list_display = ('clube', 'tipo', 'texto_pergunta', 'resposta_correta')
    list_filter = ('clube', 'tipo')
    search_fields = ('texto_pergunta', 'clube__nome')

@admin.register(PartidaMiniFanaticos)
class PartidaMiniFanaticosAdmin(admin.ModelAdmin):
    list_display = ('id', 'criador', 'status', 'clube_dupla_a', 'clube_dupla_b', 'criado_em')
    list_filter = ('status',)

@admin.register(JogadorMiniFanaticos)
class JogadorMiniFanaticosAdmin(admin.ModelAdmin):
    list_display = ('jogador', 'partida', 'dupla', 'pontos', 'tempo_gasto_segundos', 'finalizou')
    list_filter = ('dupla', 'finalizou')
    search_fields = ('jogador__username', 'jogador__first_name')
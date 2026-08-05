from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 1. AS CARTAS E OS ELENCOS (A BASE DO JOGO)
# ==========================================
class ElencoHistorico(models.Model):
    nome = models.CharField(max_length=100) # Ex: "Grêmio 2017", "Flamengo 2019"
    escudo = models.ImageField(upload_to='draft_escudos/', blank=True, null=True)

    def __str__(self):
        return self.nome

class CartaJogador(models.Model):
    POSICAO_CHOICES = [
        ('linha', 'Jogador de Linha'),
        ('goleiro', 'Goleiro')
    ]
    nome = models.CharField(max_length=100)
    elenco = models.ForeignKey(ElencoHistorico, on_delete=models.CASCADE, related_name='jogadores')
    posicao = models.CharField(max_length=10, choices=POSICAO_CHOICES)
    over = models.IntegerField(help_text="Nível de habilidade do jogador (Ex: 85)")
    foto = models.ImageField(upload_to='draft_cartas/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} (OVR {self.over}) - {self.elenco.nome}"


# ==========================================
# 2. O DRAFT DO USUÁRIO (PRANCHETA ATUAL)
# ==========================================
class MeuDraft(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Em Andamento'),
        ('eliminado', 'Eliminado ❌'),
        ('campeao', 'Campeão (Levantou a Taça!) 🏆')
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafts_x1')
    elenco_sorteado = models.ForeignKey(ElencoHistorico, on_delete=models.SET_NULL, null=True)
    goleiro = models.ForeignKey(CartaJogador, related_name='goleiro_draftado', on_delete=models.SET_NULL, null=True)
    batedores = models.ManyToManyField(CartaJogador, related_name='batedores_draftados')
    
    # Sistema de Progressão e Punição
    historico_chutes = models.CharField(max_length=255, default="", blank=True)
    vitorias_seguidas = models.IntegerField(default=0, help_text="Se chegar a 10, vira campeão!")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ativo')
    data_criacao = models.DateTimeField(auto_now_add=True)
    jogos_jogados = models.IntegerField(default=0)
    vitorias = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)

    def __str__(self):
        return f"Draft de {self.usuario.username} ({self.vitorias_seguidas}/10 vitórias) - {self.get_status_display()}"


# ==========================================
# 3. A PARTIDA (O X1) E AS COBRANÇAS
# ==========================================
class PartidaPenalti(models.Model):
    FASE_CHOICES = [
        ('aguardando', 'Aguardando Adversário'),
        ('5_cobrancas', 'Série de 5 Cobranças'),
        ('alternadas', 'Morte Súbita (Alternadas)'),
        ('finalizado', 'Jogo Encerrado')
    ]

    jogador1 = models.ForeignKey(User, related_name='partidas_j1', on_delete=models.CASCADE)
    jogador2 = models.ForeignKey(User, related_name='partidas_j2', on_delete=models.CASCADE, null=True, blank=True)
    draft_j1 = models.ForeignKey(MeuDraft, related_name='jogos_j1', on_delete=models.SET_NULL, null=True)
    draft_j2 = models.ForeignKey(MeuDraft, related_name='jogos_j2', on_delete=models.SET_NULL, null=True)
    
    # Placar e Controle de Rodadas
    placar_j1 = models.IntegerField(default=0)
    placar_j2 = models.IntegerField(default=0)
    rodada_atual = models.IntegerField(default=1) 
    fase = models.CharField(max_length=20, choices=FASE_CHOICES, default='aguardando')

    # === GATILHOS TEMPORÁRIOS DA CARTA TÁTICA ===
    j1_tatica_ativa = models.BooleanField(default=False)
    j2_tatica_ativa = models.BooleanField(default=False)
    
    # === NOVOS CAMPOS: CONTROLE DE TURNO E AÇÕES ===
    turno_batedor = models.ForeignKey(User, related_name='ataques_x1', on_delete=models.SET_NULL, null=True, blank=True)
    chutes_na_rodada = models.IntegerField(default=0) # Conta se os 2 já bateram na rodada
    ultimo_chute_zona = models.CharField(max_length=10, null=True, blank=True)
    ultima_defesa_zona = models.CharField(max_length=10, null=True, blank=True)
    ultimo_resultado = models.CharField(max_length=20, null=True, blank=True)
    
    chute_zona = models.CharField(max_length=10, null=True, blank=True)
    chute_carta_id = models.IntegerField(null=True, blank=True)
    defesa_zona = models.CharField(max_length=10, null=True, blank=True)
    defesa_carta_id = models.IntegerField(null=True, blank=True)
    # === CONFIGURAÇÕES DA SALA (REGRAS) ===
    usa_poderes = models.BooleanField(default=True)
    usa_olheiro = models.BooleanField(default=True)
    usa_emotes = models.BooleanField(default=True)
    # === CARA OU COROA ===
    # Vai guardar 'j1' ou 'j2' para sabermos quem ganhou o sorteio de bater primeiro
    moeda_sorteio = models.CharField(max_length=2, blank=True, null=True)
    # === CONTROLE DE PODERES (1 uso por jogo) ===
    j1_usou_olheiro = models.BooleanField(default=False)
    j2_usou_olheiro = models.BooleanField(default=False)
    j1_usou_poder = models.BooleanField(default=False)
    j2_usou_poder = models.BooleanField(default=False)
    emote_j1 = models.CharField(max_length=10, blank=True, null=True)
    emote_j2 = models.CharField(max_length=10, blank=True, null=True)
    
    # Fim de Jogo
    vencedor = models.ForeignKey(User, related_name='vitorias_x1', on_delete=models.SET_NULL, null=True, blank=True)
    data_partida = models.DateTimeField(auto_now_add=True)

class Cobranca(models.Model):
    ZONA_CHOICES = [
        ('se', 'Superior Esquerdo (Ângulo)'),
        ('sd', 'Superior Direito (Ângulo)'),
        ('me', 'Centro (Meio do Gol)'),
        ('ie', 'Inferior Esquerdo (Rasteiro)'),
        ('id', 'Inferior Direito (Rasteiro)')
    ]
    RESULTADO_CHOICES = [
        ('gol', 'Golaço! ⚽'),
        ('defesa', 'Goleiro Espalmou! 🧤'),
        ('frango', 'Passou por baixo! (Frango) 🐓'),
        ('trave', 'Na Trave! 🥅'),
        ('isolou', 'Mandou na Lua! 🚀')
    ]

    partida = models.ForeignKey(PartidaPenalti, on_delete=models.CASCADE, related_name='cobrancas')
    rodada = models.IntegerField() # Para saber se é a cobrança 1, 2... ou 6 (alternadas)
    
    # Quem bate e quem defende nesta cobrança específica
    usuario_batedor = models.ForeignKey(User, related_name='meus_chutes', on_delete=models.CASCADE)
    carta_batedor = models.ForeignKey(CartaJogador, related_name='historico_chutes', on_delete=models.CASCADE)
    carta_goleiro = models.ForeignKey(CartaJogador, related_name='historico_defesas', on_delete=models.CASCADE)
    
    # Decisões salvas via AJAX
    alvo_chute = models.CharField(max_length=2, choices=ZONA_CHOICES, null=True, blank=True)
    pulo_goleiro = models.CharField(max_length=2, choices=ZONA_CHOICES, null=True, blank=True)
    
    # O resultado que a matemática do Backend vai decidir
    resultado = models.CharField(max_length=15, choices=RESULTADO_CHOICES, null=True, blank=True)



class EstatisticaJogador(models.Model):
    """Um 'card' de jogador de futebol usado nos duelos do minijogo."""

    nome = models.CharField(max_length=100)
    clube = models.CharField(max_length=100, blank=True, help_text="Ex: Real Madrid, Flamengo...")
    posicao = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('GOL', 'Goleiro'),
            ('ZAG', 'Zagueiro'),
            ('LAT', 'Lateral'),
            ('MEI', 'Meio-campo'),
            ('ATA', 'Atacante'),
        ],
    )
    foto = models.ImageField(upload_to='minijogo/jogadores/')

    gols = models.PositiveIntegerField(default=0)
    assistencias = models.PositiveIntegerField(default=0)
    cartoes_amarelos = models.PositiveIntegerField(default=0)
    cartoes_vermelhos = models.PositiveIntegerField(default=0)
    jogos = models.PositiveIntegerField(default=0, help_text="Total de partidas na carreira")
    titulos = models.PositiveIntegerField(default=0, help_text="Total de títulos oficiais na carreira")

    ativo = models.BooleanField(default=True, help_text="Desmarque para tirar o jogador do jogo sem apagá-lo")

    class Meta:
        verbose_name = "Estatística de Jogador"
        verbose_name_plural = "Estatísticas de Jogadores"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.clube})" if self.clube else self.nome

    @property
    def cartoes(self):
        """Total de cartões (amarelos + vermelhos), usado como uma das categorias do duelo."""
        return self.cartoes_amarelos + self.cartoes_vermelhos


class RankingMinijogo(models.Model):
    """Registra o resultado de cada partida jogada (fim de jogo = uma linha nova)."""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_minijogo')
    pontuacao = models.PositiveIntegerField(default=0)
    maior_sequencia = models.PositiveIntegerField(default=0, help_text="Maior sequência de acertos seguidos na partida")
    data_partida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Partida do Ranking"
        verbose_name_plural = "Ranking do Minijogo"
        ordering = ['-pontuacao']

    def __str__(self):
        return f"{self.usuario.username} - {self.pontuacao} pts"

class EsquadraoHistorico(models.Model):
    """Cards de Clubes/Temporadas específicas para o minijogo."""
    nome = models.CharField(max_length=100, help_text="Ex: Galo 2013, Flamengo 2019")
    clube = models.CharField(max_length=100, help_text="Nome do clube para buscar o escudo genérico se precisar")
    ano = models.IntegerField()
    escudo = models.ImageField(upload_to='minijogo/escudos_esquadroes/', blank=True, null=True)
    
    gols_pro = models.PositiveIntegerField(default=0, help_text="Gols marcados na temporada")
    gols_sofridos = models.PositiveIntegerField(default=0, help_text="Gols sofridos na temporada")
    titulos = models.PositiveIntegerField(default=0, help_text="Títulos conquistados nesta temporada específica")
    
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Esquadrão Histórico"
        verbose_name_plural = "Esquadrões Históricos"
        ordering = ['-ano', 'nome']

    def __str__(self):
        return self.nome

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
    vitorias_seguidas = models.IntegerField(default=0, help_text="Se chegar a 10, vira campeão!")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ativo')
    data_criacao = models.DateTimeField(auto_now_add=True)

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

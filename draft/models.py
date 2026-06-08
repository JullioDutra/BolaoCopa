from django.db import models
from django.contrib.auth.models import User

# ==========================================
# MODO DRAFT: COPA DO BRASIL HISTÓRICA
# ==========================================

class ClubeBrasileiro(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Clube (Ex: Flamengo)")
    escudo = models.ImageField(upload_to='escudos_draft/', blank=True, null=True)

    def __str__(self):
        return self.nome

class ElencoHistorico(models.Model):
    clube = models.ForeignKey(ClubeBrasileiro, on_delete=models.CASCADE, related_name='elencos')
    ano = models.IntegerField(verbose_name="Ano do Elenco (Ex: 2019)")
    forca_base = models.IntegerField(default=80, verbose_name="Força do Time na Época")
    
    class Meta:
        unique_together = ('clube', 'ano') # Evita cadastrar o mesmo time no mesmo ano duas vezes

    def __str__(self):
        return f"{self.clube.nome} de {self.ano}"

class JogadorDraft(models.Model):
    POSICOES_CHOICES = [
        ('GOL', 'Goleiro'),
        ('ZAG', 'Zagueiro'),
        ('LAT', 'Lateral'),
        ('VOL', 'Volante'),
        ('MEI', 'Meia'),
        ('ATA', 'Atacante'),
    ]
    
    elenco = models.ForeignKey(ElencoHistorico, on_delete=models.CASCADE, related_name='jogadores')
    nome = models.CharField(max_length=100, verbose_name="Nome do Jogador")
    posicao = models.CharField(max_length=3, choices=POSICOES_CHOICES)
    nota_geral = models.IntegerField(verbose_name="Overall (OVR)")
    nota_ataque = models.IntegerField(default=50)
    nota_defesa = models.IntegerField(default=50)
    foto = models.ImageField(upload_to='jogadores_draft/', blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.posicao}) - {self.elenco}"

class SessaoDraft(models.Model):
    STATUS_CHOICES = [
        ('montando', 'Montando Elenco'),
        ('jogando', 'Disputando a Copa'),
        ('eliminado', 'Eliminado'),
        ('campeao', 'Campeão'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meus_drafts')
    formacao = models.CharField(max_length=10, default='4-3-3', verbose_name="Formação Tática")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='montando')
    fase_atual = models.IntegerField(default=1, verbose_name="Fase da Copa (1 a 5)")
    data_inicio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Draft de {self.usuario.username} ({self.formacao})"

class EscolhaDraft(models.Model):
    """Guarda qual jogador o usuário escolheu e em qual posição ele o colocou na prancheta"""
    sessao = models.ForeignKey(SessaoDraft, on_delete=models.CASCADE, related_name='escolhas')
    jogador = models.ForeignKey(JogadorDraft, on_delete=models.CASCADE)
    posicao_escalada = models.CharField(max_length=20, verbose_name="Posição na Prancheta (Ex: Zagueiro 1)")

    def __str__(self):
        return f"{self.jogador.nome} escalado como {self.posicao_escalada}"
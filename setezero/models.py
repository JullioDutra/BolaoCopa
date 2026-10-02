import uuid

from django.contrib.auth.models import User
from django.db import models


class Temporada7a0(models.Model):
    """ Campeonato de pontos corridos (ida e volta) entre 8 times históricos. """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='temporadas_7a0')
    time_usuario = models.CharField(max_length=30)
    estado = models.JSONField(default=dict)   # times, calendario, rodada, tabela, resultados
    status = models.CharField(max_length=12, default='andamento')   # andamento | finalizada
    posicao_final = models.PositiveSmallIntegerField(null=True, blank=True)
    premio = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"Temporada de {self.usuario} com {self.time_usuario}"


class DraftCopa7a0(models.Model):
    """ Draft: o usuário monta o XI sorteando times históricos e disputa uma Copa do Brasil de 7 jogos. """
    STATUS = [('montando', 'Montando o time'), ('copa', 'Copa em andamento'), ('campeao', 'Campeão'),
              ('eliminado', 'Eliminado'), ('terminou', 'Campanha encerrada')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drafts_7a0')
    codigo = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    formacao = models.CharField(max_length=10, default='4-3-3')
    mentalidade = models.CharField(max_length=12, default='equilibrado')
    eliminatorio = models.BooleanField(default=True, help_text="Mata-mata: perdeu, está fora. Campanha: joga os 7 jogos de qualquer jeito.")
    estado = models.JSONField(default=dict)    # slots, banco, sorteadas, pendente, skips, rivais
    status = models.CharField(max_length=10, choices=STATUS, default='montando')
    fase = models.PositiveSmallIntegerField(default=0)       # próxima fase a jogar (0..6)
    campanha = models.JSONField(default=list)                 # resultado de cada fase jogada
    invicto = models.BooleanField(default=False)              # campeão sem derrota e sem pênaltis
    premio = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"Draft de {self.usuario} ({self.get_status_display()})"


class Partida7a0(models.Model):
    MODOS = [('amistoso', 'Amistoso histórico'), ('desafio', 'Desafio 7 a 0'), ('temporada', 'Temporada'),
             ('copa', 'Draft Copa do Brasil')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_7a0')
    modo = models.CharField(max_length=10, choices=MODOS, default='amistoso')
    draft = models.ForeignKey(DraftCopa7a0, null=True, blank=True, on_delete=models.CASCADE, related_name='partidas')
    temporada = models.ForeignKey(Temporada7a0, null=True, blank=True, on_delete=models.CASCADE, related_name='partidas')
    rodada = models.PositiveSmallIntegerField(null=True, blank=True)
    lado_usuario = models.CharField(max_length=4, default='casa')   # casa | fora
    time_usuario = models.CharField(max_length=30)
    time_rival = models.CharField(max_length=30)
    estado = models.JSONField(default=dict)
    status = models.CharField(max_length=10, default='pre')   # pre | jogando | intervalo | fim
    gols_usuario = models.PositiveSmallIntegerField(default=0)
    gols_rival = models.PositiveSmallIntegerField(default=0)
    resultado = models.CharField(max_length=1, blank=True)   # V | E | D
    fase = models.PositiveSmallIntegerField(null=True, blank=True)   # só no draft
    premio = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.time_usuario} {self.gols_usuario} x {self.gols_rival} {self.time_rival}"

    @property
    def saldo(self):
        return self.gols_usuario - self.gols_rival

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


class Partida7a0(models.Model):
    MODOS = [('amistoso', 'Amistoso histórico'), ('desafio', 'Desafio 7 a 0'), ('temporada', 'Temporada')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_7a0')
    modo = models.CharField(max_length=10, choices=MODOS, default='amistoso')
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

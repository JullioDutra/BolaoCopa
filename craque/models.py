from django.contrib.auth.models import User
from django.db import models


class Carreira(models.Model):
    """ A carreira de um jogador fictício no "Vida de Craque". Uma ativa por usuário. """
    STATUS = [('ativa', 'Ativa'), ('encerrada', 'Encerrada')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carreiras_craque')
    semente = models.BigIntegerField()
    estado = models.JSONField(default=dict)       # jogador, atributos, medidores, temporada atual e carreira
    pendente = models.JSONField(default=dict)     # a decisão da vez: cena, coletiva, fim de temporada, aposentadoria
    historico = models.JSONField(default=list)    # linha do tempo: decisões, jogos, coletivas, temporadas
    status = models.CharField(max_length=10, choices=STATUS, default='ativa')
    pontuacao = models.PositiveIntegerField(default=0)
    premio_total = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-atualizado_em']
        verbose_name = 'Carreira (Vida de Craque)'
        verbose_name_plural = 'Carreiras (Vida de Craque)'

    def __str__(self):
        return f"{self.estado.get('nome', '?')} ({self.usuario}) · {self.status}"

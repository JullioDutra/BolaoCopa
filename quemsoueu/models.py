from django.contrib.auth.models import User
from django.db import models


class PartidaQSE(models.Model):
    """ Uma rodada do "Quem Sou Eu?": o desafio do dia (um por usuário) ou um treino livre. """
    MODOS = [('diario', 'Desafio do dia'), ('treino', 'Treino')]
    STATUS = [('jogando', 'Jogando'), ('acertou', 'Acertou'), ('errou', 'Errou'), ('desistiu', 'Desistiu')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_qse')
    modo = models.CharField(max_length=8, choices=MODOS, default='diario')
    dia = models.DateField()
    craque = models.CharField(max_length=40)
    perguntas = models.JSONField(default=list)   # [{texto, resposta, comentario, fonte: rapida|ia}]
    palpites = models.JSONField(default=list)    # palpites errados, em texto
    dicas = models.JSONField(default=list)       # textos das dicas já reveladas
    status = models.CharField(max_length=10, choices=STATUS, default='jogando')
    pontos = models.PositiveSmallIntegerField(default=0)
    premio = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Partida do Quem Sou Eu?'
        verbose_name_plural = 'Partidas do Quem Sou Eu?'

    def __str__(self):
        return f'{self.usuario} · {self.get_modo_display()} {self.dia} · {self.status}'

    @property
    def terminou(self):
        return self.status != 'jogando'

from django.contrib.auth.models import User
from django.db import models


class UsoIA(models.Model):
    """ Quantas chamadas de IA cada usuário fez no dia (limite em settings.IA_LIMITE_DIARIO) e quanto custaram em tokens. """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uso_ia')
    dia = models.DateField()
    chamadas = models.PositiveIntegerField(default=0)
    tokens_entrada = models.PositiveIntegerField(default=0)
    tokens_saida = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('usuario', 'dia')]
        ordering = ['-dia']
        verbose_name = 'Uso de IA'
        verbose_name_plural = 'Uso de IA'

    def __str__(self):
        return f'{self.usuario} · {self.dia}: {self.chamadas} chamadas'

import uuid

from django.contrib.auth.models import User
from django.db import models


class PartidaCabecudos(models.Model):
    """ Uma partida do Cabeçudos. O jogo roda no navegador; o servidor só aceita resultados plausíveis. """
    STATUS = [('jogando', 'Jogando'), ('vitoria', 'Vitória'), ('empate', 'Empate'), ('derrota', 'Derrota'),
              ('invalida', 'Inválida')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_cabecudos')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    fase = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=10, choices=STATUS, default='jogando')
    gols_pro = models.PositiveSmallIntegerField(default=0)
    gols_contra = models.PositiveSmallIntegerField(default=0)
    premio = models.PositiveIntegerField(default=0)
    iniciada_em = models.DateTimeField(auto_now_add=True)
    finalizada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-iniciada_em']
        verbose_name = 'Partida do Cabeçudos'
        verbose_name_plural = 'Partidas do Cabeçudos'

    def __str__(self):
        return f'{self.usuario} · fase {self.fase} · {self.gols_pro}x{self.gols_contra} ({self.status})'

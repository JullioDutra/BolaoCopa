from django.contrib.auth.models import User
from django.db import models


class PartidaArbitro(models.Model):
    """ Uma partida do Apito Final: 10 lances para apitar, com gabarito guardado só no servidor. """
    STATUS = [('andamento', 'Em andamento'), ('fim', 'Finalizada')]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partidas_arbitro')
    semente = models.BigIntegerField()
    lances = models.JSONField(default=list)       # lances completos (com resposta certa e explicação)
    respostas = models.JSONField(default=list)    # uma entrada por lance já apitado
    indice = models.PositiveSmallIntegerField(default=0)            # lance atual (0..9)
    inicio_lance = models.DateTimeField(null=True, blank=True)      # quando o lance atual foi servido
    var_usado = models.BooleanField(default=False)                  # VAR chamado no lance atual
    sequencia = models.PositiveSmallIntegerField(default=0)
    melhor_sequencia = models.PositiveSmallIntegerField(default=0)
    pontos = models.PositiveIntegerField(default=0)
    acertos = models.PositiveSmallIntegerField(default=0)
    vars_chamados = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS, default='andamento')
    premio = models.PositiveIntegerField(default=0)
    resenha = models.JSONField(default=dict, blank=True)    # comentário do narrador/comentarista (IA) no fim
    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Partida do Apito Final'
        verbose_name_plural = 'Partidas do Apito Final'

    def __str__(self):
        return f'{self.usuario} · {self.pontos} pts ({self.acertos}/{self.total})'

    @property
    def total(self):
        return len(self.lances)

    @property
    def precisao(self):
        feitos = len(self.respostas)
        return round(100 * self.acertos / feitos) if feitos else 0

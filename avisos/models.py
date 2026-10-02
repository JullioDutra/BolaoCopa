from django.contrib.auth.models import User
from django.db import models


class PushSubscription(models.Model):
    """ Um aparelho/navegador que aceitou receber notificações push. """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.URLField(max_length=600, unique=True)
    p256dh = models.CharField(max_length=200)
    auth = models.CharField(max_length=100)
    aparelho = models.CharField(max_length=120, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    ultimo_envio_ok = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} — {self.aparelho or 'aparelho'}"


class Notificacao(models.Model):
    """ Caixa de entrada dentro do site (funciona mesmo sem push). `chave` evita avisos repetidos. """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=120)
    texto = models.CharField(max_length=300, blank=True)
    url = models.CharField(max_length=300, default='/')
    tipo = models.CharField(max_length=20, default='geral')
    chave = models.CharField(max_length=80, blank=True, help_text="Identificador único por usuário (ex.: lembrete:123)")
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em', '-id']
        constraints = [
            models.UniqueConstraint(fields=['usuario', 'chave'], condition=~models.Q(chave=''), name='aviso_unico_por_chave'),
        ]

    def __str__(self):
        return f"{self.usuario.username}: {self.titulo}"


class Atividade(models.Model):
    """ Feed público "Resenha ao vivo": fatos curiosos que acontecem no app. """
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='atividades')
    tipo = models.CharField(max_length=20, default='geral')
    texto = models.CharField(max_length=200)
    url = models.CharField(max_length=300, blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em', '-id']
        verbose_name_plural = 'Atividades'

    def __str__(self):
        return self.texto


class Conquista(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conquistas')
    slug = models.CharField(max_length=40)
    desbloqueada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('usuario', 'slug')]
        ordering = ['-desbloqueada_em']

    def __str__(self):
        return f"{self.usuario.username}: {self.slug}"

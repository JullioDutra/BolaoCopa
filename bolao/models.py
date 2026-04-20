from django.db import models
from django.contrib.auth.models import User

class Participacao(models.Model):
    TIPO_CHOICES = [
        ('resenha', 'Modo Resenha (Livre)'),
        ('pago', 'Modo Pago (Premiado)')
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='participacao')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='resenha')
    aprovado = models.BooleanField(default=False)
    data_adesao = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Modo resenha já entra aprovado automaticamente
        if self.tipo == 'resenha':
            self.aprovado = True
        super().save(*args, **kwargs)

    def __str__(self):
        status = "Liberado" if self.aprovado else "Pendente"
        return f"{self.usuario.username} | {self.get_tipo_display()} | {status}"
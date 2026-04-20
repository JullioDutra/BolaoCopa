from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Carteira.objects.create(usuario=instance)

class Carteira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carteira')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Carteira de {self.usuario.username} - Saldo: R$ {self.saldo}"

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('deposito', 'Depósito (Pix)'),
        ('aposta', 'Participação Bolão/Convocação'),
        ('premio', 'Premiação Recebida'),
        ('saque', 'Retirada de Saldo'),
    ]
    
    carteira = models.ForeignKey(Carteira, on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} ({self.carteira.usuario.username})"
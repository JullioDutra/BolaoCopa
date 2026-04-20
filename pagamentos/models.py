from django.db import models
from django.contrib.auth.models import User

class Deposito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='depositos')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    aprovado = models.BooleanField(default=False)
    
    # Campo opcional caso queira que o usuário envie o print do Pix
    comprovante = models.ImageField(upload_to='comprovantes/', blank=True, null=True)

    def __str__(self):
        status = "✅ Aprovado" if self.aprovado else "⏳ Pendente"
        return f"{self.usuario.username} - R$ {self.valor} ({status})"
    

class Saque(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saques')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    chave_pix = models.CharField(max_length=100, verbose_name="Sua Chave Pix")
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        status = "✅ Pago" if self.aprovado else "⏳ Pendente"
        return f"Saque: {self.usuario.username} - R$ {self.valor} ({status})"
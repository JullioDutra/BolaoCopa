from django.db import models
from django.contrib.auth.models import User

class Jogador(models.Model):
    # Base de dados de jogadores reais para o usuário escolher
    nome = models.CharField(max_length=100)
    posicao = models.CharField(max_length=50)
    clube_atual = models.CharField(max_length=100, blank=True, null=True)
    modalidade = models.CharField(max_length=10, choices=[('resenha', 'Resenha'), ('pago', 'Pago')], default='resenha')
    foto = models.ImageField(upload_to='jogadores/', blank=True, null=True)
    convocado_oficial = models.BooleanField(default=False, help_text="Marque esta opção quando o técnico oficializar a convocação na vida real.")
    
    def __str__(self):
        return f"{self.nome} ({self.posicao})"

class Convocacao(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='convocacao')
    jogadores = models.ManyToManyField(Jogador, related_name='convocados')
    data_atualizacao = models.DateTimeField(auto_now=True)

    def total_convocados(self):
        return self.jogadores.count()

    def __str__(self):
        return f"Convocação de {self.usuario.username} ({self.total_convocados()}/26)"  
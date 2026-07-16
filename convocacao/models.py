from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Jogador(models.Model):
    POSICOES_CHOICES = [
        ('Goleiro', 'Goleiro'),
        ('Defensor', 'Defensor (Zagueiro/Lateral)'),
        ('Meio-campista', 'Meio-campista'),
        ('Atacante', 'Atacante'),
    ]

    # Base de dados de jogadores reais para o usuário escolher
    nome = models.CharField(max_length=100)
    posicao = models.CharField(max_length=50, choices=POSICOES_CHOICES)
    clube_atual = models.CharField(max_length=100, blank=True, null=True)
    modalidade = models.CharField(max_length=10, choices=[('resenha', 'Resenha'), ('pago', 'Pago')], default='resenha')
    foto = models.ImageField(upload_to='jogadores/', blank=True, null=True)
    convocado_oficial = models.BooleanField(default=False, help_text="Marque se este jogador faz parte da seleção final do campeonato.")
    pontos_obtidos = models.IntegerField(default=0, help_text="Pontos ganhos por acertar esse jogador.")
    
    def __str__(self):
        return f"{self.nome} ({self.posicao})"

class Convocacao(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='selecao_brasileirao')
    jogadores = models.ManyToManyField(Jogador, related_name='convocados')
    data_atualizacao = models.DateTimeField(auto_now=True)
    pontuacao_total = models.IntegerField(default=0)

    def total_convocados(self):
        return self.jogadores.count()
    
    def verifica_formacao_433(self):
        """Verifica se os jogadores selecionados formam exatamente um 4-3-3"""
        goleiros = self.jogadores.filter(posicao='Goleiro').count()
        defensores = self.jogadores.filter(posicao='Defensor').count()
        meias = self.jogadores.filter(posicao='Meio-campista').count()
        atacantes = self.jogadores.filter(posicao='Atacante').count()
        
        return (goleiros == 1 and defensores == 4 and meias == 3 and atacantes == 3)

    def __str__(self):
        status = "✅ 4-3-3" if self.verifica_formacao_433() else "❌ Inválido"
        return f"Seleção de {self.usuario.username} ({self.total_convocados()}/11) - {status}"

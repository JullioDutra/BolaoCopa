from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Clube(models.Model):
    """Banco centralizado de Escudos de Clubes"""
    nome = models.CharField(max_length=100, unique=True)
    escudo = models.ImageField(upload_to='duelos/clubes/')
    
    def __str__(self): 
        return self.nome

class JogadorBanco(models.Model):
    """Banco centralizado de Nomes de Jogadores (Para o Autocomplete)"""
    nome = models.CharField(max_length=100, unique=True)
    
    def __str__(self): 
        return self.nome

class CategoriaDesafio(models.Model):
    TIPO_CHOICES = [
        ('elenco', 'Elencos clássicos'),
        ('trajetoria', 'Jogo da trajetória'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=150) 
    resposta_oculta = models.CharField(max_length=150, blank=True, null=True) 

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo}"

class ItemDesafio(models.Model):
    categoria = models.ForeignKey(CategoriaDesafio, on_delete=models.CASCADE, related_name='itens')
    
    # NOVOS CAMPOS PARA OS BANCOS:
    clube_vinculado = models.ForeignKey(Clube, on_delete=models.SET_NULL, null=True, blank=True, help_text="Selecione do banco de escudos")
    jogador_vinculado = models.ForeignKey(JogadorBanco, on_delete=models.SET_NULL, null=True, blank=True, help_text="Selecione do banco de jogadores")
    
    # CAMPOS ANTIGOS MANTIDOS (Para não apagar o que já cadastrou)
    nome = models.CharField(max_length=100, blank=True, null=True) 
    imagem = models.ImageField(upload_to='duelos/itens/', blank=True, null=True)
    
    posicao_tatica = models.CharField(max_length=50, blank=True) 
    ordem = models.IntegerField(default=0) 

    class Meta:
        ordering = ['ordem']

    def get_nome(self):
        """Inteligência que busca o nome no banco ou no campo manual"""
        if self.jogador_vinculado: return self.jogador_vinculado.nome
        if self.clube_vinculado: return self.clube_vinculado.nome
        return self.nome or ""

    def get_imagem_url(self):
        """Inteligência que busca a imagem no banco de clubes ou no manual"""
        if self.clube_vinculado and self.clube_vinculado.escudo:
            return self.clube_vinculado.escudo.url
        if self.imagem:
            return self.imagem.url
        return ""

    def __str__(self):
        return f"{self.get_nome()} - {self.categoria.titulo}"

class PartidaDuelo(models.Model):
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando Oponente'),
        ('andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado')
    ]
    categoria = models.ForeignKey(CategoriaDesafio, on_delete=models.CASCADE)
    jogador_criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duelos_criados')
    jogador_convidado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duelos_aceitos', null=True, blank=True)
    turno_de = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meu_turno_duelo', null=True, blank=True)
    turno_iniciado_em = models.DateTimeField(auto_now_add=True)
    pontos_criador = models.IntegerField(default=0)
    pontos_convidado = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='aguardando', choices=STATUS_CHOICES)
    itens_revelados = models.ManyToManyField(ItemDesafio, blank=True)
    erros_acumulados = models.IntegerField(default=0) 
    vencedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duelos_vencidos', null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        j2_nome = self.jogador_convidado.first_name if self.jogador_convidado else "???"
        return f"{self.jogador_criador.first_name} vs {j2_nome} ({self.categoria.titulo})"
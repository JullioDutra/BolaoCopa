from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class CategoriaDesafio(models.Model):
    TIPO_CHOICES = [
        ('elenco', 'Elenco Histórico (Ex: Itália 2006)'),
        ('trajetoria', 'Trajetória de Clubes'),
    ]
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Ex: "Itália 2006" (para elenco) ou "Jogador Misterioso 1" (para trajetória)
    titulo = models.CharField(max_length=150) 
    
    # Preenchido APENAS se for trajetória (Ex: "Ronaldinho Gaúcho"). No elenco, a resposta é o próprio item.
    resposta_oculta = models.CharField(max_length=150, blank=True, null=True) 

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo}"

class ItemDesafio(models.Model):
    categoria = models.ForeignKey(CategoriaDesafio, on_delete=models.CASCADE, related_name='itens')
    
    # Nome do jogador (Ex: "Buffon") ou Nome do Clube (Ex: "PSG")
    nome = models.CharField(max_length=100) 
    
    # Útil para os escudos na trajetória ou fotos dos jogadores no campinho
    imagem = models.ImageField(upload_to='duelos/itens/', blank=True, null=True)
    
    # Para o Campinho: ex: "goleiro", "zagueiro-1", "atacante-2" (Usaremos no CSS depois)
    posicao_tatica = models.CharField(max_length=50, blank=True) 
    
    # Para a Trajetória: 1 (Primeiro clube), 2 (Segundo clube), etc.
    ordem = models.IntegerField(default=0) 

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.nome} - {self.categoria.titulo}"

class PartidaDuelo(models.Model):
    STATUS_CHOICES = [
        ('aguardando', 'Aguardando Oponente'),
        ('andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado')
    ]

    categoria = models.ForeignKey(CategoriaDesafio, on_delete=models.CASCADE)
    
    # Jogadores
    jogador_criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duelos_criados')
    jogador_convidado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duelos_aceitos', null=True, blank=True)
    
    # O Segredo do PythonAnywhere: Controle de Turnos e Tempo sem WebSockets
    turno_de = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meu_turno_duelo', null=True, blank=True)
    turno_iniciado_em = models.DateTimeField(auto_now_add=True)
    
    # Placar e Controle
    pontos_criador = models.IntegerField(default=0)
    pontos_convidado = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='aguardando', choices=STATUS_CHOICES)
    
    # Progresso: O que já foi acertado (elenco) ou revelado (escudos da trajetória)
    itens_revelados = models.ManyToManyField(ItemDesafio, blank=True)
    
    # Quantos erros já aconteceram neste turno/rodada (Muda a lógica da trajetória)
    erros_acumulados = models.IntegerField(default=0) 
    
    vencedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duelos_vencidos', null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        j2_nome = self.jogador_convidado.username if self.jogador_convidado else "???"
        return f"{self.jogador_criador.username} vs {j2_nome} ({self.categoria.titulo})"
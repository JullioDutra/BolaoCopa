from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import random
import json

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

# ==========================================
# MODO CAMPEONATO (MATA-MATA)
# ==========================================

class Campeonato(models.Model):
    STATUS_CHOICES = (
        ('inscricoes', 'Inscrições Abertas'),
        ('andamento', 'Em Andamento'),
        ('finalizado', 'Finalizado'),
    )

    nome = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campeonatos_criados')
    data_limite_inscricao = models.DateTimeField(help_text="Data e hora que as inscrições se encerram.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inscricoes')
    codigo_convite = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.get_status_display()}"

    def inscricoes_abertas(self):
        return self.status == 'inscricoes' and timezone.now() < self.data_limite_inscricao

class InscricaoCampeonato(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='inscritos')
    jogador = models.ForeignKey(User, on_delete=models.CASCADE)
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('campeonato', 'jogador') # Evita que o cara se inscreva duas vezes

    def __str__(self):
        return f"{self.jogador.username} em {self.campeonato.nome}"

class ConfrontoCampeonato(models.Model):
    FASES_CHOICES = (
        ('oitavas', 'Oitavas de Final'),
        ('quartas', 'Quartas de Final'),
        ('semi', 'Semifinal'),
        ('final', 'Grande Final'),
    )

    STATUS_CONFRONTO = (
        ('aguardando', 'Aguardando Adversário/Jogadores'),
        ('andamento', 'Bola Rolando'),
        ('finalizado', 'Finalizado'),
        ('wo', 'Vencedor por W.O.'),
    )

    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='confrontos')
    fase = models.CharField(max_length=20, choices=FASES_CHOICES)
    
    # Jogadores da chave
    jogador1 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='confrontos_como_j1')
    jogador2 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confrontos_como_j2')
    vencedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='confrontos_vencidos')
    
    # O jogo sorteado para este confronto
    desafio_sorteado = models.ForeignKey('CategoriaDesafio', on_delete=models.SET_NULL, null=True, blank=True)
    
    # A partida em si (ligando com a lógica de duelos que você já tem)
    partida_vinculada = models.OneToOneField('PartidaDuelo', on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CONFRONTO, default='aguardando')
    ordem_chave = models.IntegerField(default=0, help_text="Para organizar o desenho do chaveamento no front-end")

    def __str__(self):
        j1 = self.jogador1.username if self.jogador1 else 'TBD'
        j2 = self.jogador2.username if self.jogador2 else 'TBD'
        return f"{self.campeonato.nome} [{self.get_fase_display()}]: {j1} x {j2}"



# ==========================================
# MODO MINI FANÁTICOS (2v2)
# ==========================================
""""
class ClubeFutebol(models.Model):
    """Tabela com os times para a dupla escolher como 'Time do Coração'."""
    nome = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nome

class PerguntaClube(models.Model):
    """O banco de questões de cada time (Múltipla Escolha ou Aberta)."""
    TIPOS_PERGUNTA = (
        ('multipla', 'Múltipla Escolha'),
        ('aberta', 'Resposta Aberta (Texto)'),
    )
    
    clube = models.ForeignKey(ClubeFutebol, on_delete=models.CASCADE, related_name='perguntas')
    tipo = models.CharField(max_length=20, choices=TIPOS_PERGUNTA, default='multipla')
    texto_pergunta = models.TextField(help_text="Ex: Qual jogador foi artilheiro em 2013?")
    
    # Campos para Múltipla Escolha (Se for 'aberta', ficam vazios)
    opcao_a = models.CharField(max_length=255, blank=True, null=True)
    opcao_b = models.CharField(max_length=255, blank=True, null=True)
    opcao_c = models.CharField(max_length=255, blank=True, null=True)
    opcao_d = models.CharField(max_length=255, blank=True, null=True)
    
    # A resposta correta. Se for múltipla, guarde 'A', 'B', 'C' ou 'D'. 
    # Se for aberta, guarde o nome exato (ex: 'Ronaldinho', 'Reinaldo').
    resposta_correta = models.CharField(max_length=255)

    def __str__(self):
        return f"[{self.clube.nome}] {self.texto_pergunta[:40]}..."

class PartidaMiniFanaticos(models.Model):
    """A mesa da partida 2v2."""
    criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mini_criadas')
    status = models.CharField(max_length=20, default='aguardando') # aguardando, andamento, finalizado
    
    # Os times escolhidos por cada dupla na sala de espera
    clube_dupla_a = models.ForeignKey(ClubeFutebol, on_delete=models.SET_NULL, null=True, blank=True, related_name='partidas_a')
    clube_dupla_b = models.ForeignKey(ClubeFutebol, on_delete=models.SET_NULL, null=True, blank=True, related_name='partidas_b')
    
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mini Fanáticos #{self.id} - Status: {self.status}"

class JogadorMiniFanaticos(models.Model):
    """Representa cada um dos 4 jogadores dentro da sala."""
    partida = models.ForeignKey(PartidaMiniFanaticos, on_delete=models.CASCADE, related_name='jogadores')
    jogador = models.ForeignKey(User, on_delete=models.CASCADE)
    dupla = models.CharField(max_length=1, choices=(('A', 'Dupla A'), ('B', 'Dupla B')))
    
    # O Placar e o Desempate
    pontos = models.IntegerField(default=0)
    tempo_gasto_segundos = models.FloatField(default=0.0)
    
    # Controle para saber quando o jogador terminou de responder tudo
    finalizou = models.BooleanField(default=False)

    class Meta:
        # Garante que o mesmo jogador não entre duas vezes na mesma partida
        unique_together = ('partida', 'jogador')

    def __str__(self):
        return f"{self.jogador.username} - Dupla {self.dupla}"
    

"""
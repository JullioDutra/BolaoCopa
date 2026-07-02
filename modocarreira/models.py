from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ServidorConfig(models.Model):
    """ Singleton de controle temporal e fases globais do ecossistema """
    temporada_atual = models.IntegerField(default=1)
    rodada_atual = models.IntegerField(default=1)
    fase_mercado_aberto = models.BooleanField(default=True)
    periodo_data_fifa = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Configuração do Servidor"
        verbose_name_plural = "Configurações do Servidor"

class Campeonato(models.Model):
    """ Estrutura das competições vigentes (Séries A/B/C, Copa e Continentais) """
    TIPOS = [('liga', 'Pontos Corridos'), ('mata_mata', 'Eliminatória')]
    DIVISOES = [('A', 'Série A'), ('B', 'Série B'), ('C', 'Série C'), ('INT', 'Internacional/Copa')]

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15, choices=TIPOS)
    divisao = models.CharField(max_length=3, choices=DIVISOES)
    temporada = models.IntegerField()

    def __str__(self):
        return f"{self.nome} - Temp. {self.temporada}"

class Clube(models.Model):
    """ Entidade dos times que disputam as competições do universo """
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=3)
    divisao = models.CharField(max_length=3, choices=Campeonato.DIVISOES, default='C')
    escudo = models.ImageField(upload_to='escudos_carreira/', null=True, blank=True)
    orcamento = models.BigIntegerField(default=500000)
    prestigio_reputacao = models.IntegerField(default=50) 

    def __str__(self):
        return self.nome

class ClassificacaoLiga(models.Model):
    """ Tabela de pontuação de torneios em formato de pontos corridos """
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='tabela_posicoes')
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)
    pontos = models.IntegerField(default=0)
    jogos = models.IntegerField(default=0)
    vitorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    gols_pro = models.IntegerField(default=0)
    gols_contra = models.IntegerField(default=0)

    class Meta:
        ordering = ['-pontos', '-vitorias', '-gols_pro']

class MarcaPatrocinadora(models.Model):
    nome = models.CharField(max_length=50)
    reputacao_minima_exigida = models.IntegerField(default=20)
    bonus_tecnica = models.IntegerField(default=0)
    bonus_fisico = models.IntegerField(default=0)
    reducao_risco_lesao = models.IntegerField(default=0)

    def __str__(self):
        return self.nome

class PatrocinioContrato(models.Model):
    avatar = models.ForeignKey('Avatar', on_delete=models.CASCADE, related_name='patrocinios')
    marca = models.ForeignKey(MarcaPatrocinadora, on_delete=models.CASCADE)
    valor_por_rodada = models.IntegerField()
    temporada_inicio = models.IntegerField()
    duracao_temporadas = models.IntegerField()
    ativo = models.BooleanField(default=True)

class Avatar(models.Model):
    ARQUETIPOS = [('xerife', 'Zagueiro Xerife'), ('maestro', 'Meia Maestro'), ('matador', 'Atacante Matador'), ('motorzinho', 'Ponta Ligeiro')]
    POSICOES_TATICAS = [('GK', 'Goleiro'), ('CB', 'Zagueiro'), ('LB', 'Lateral Esquerdo'), ('RB', 'Lateral Direito'), ('DM', 'Volante'), ('CM', 'Meia Central'), ('AM', 'Meia Armador'), ('LW', 'Ponta Esquerda'), ('RW', 'Ponta Direita'), ('ST', 'Centroavante')]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='avatar_carreira')
    nome_camisa = models.CharField(max_length=20)
    arquetipo = models.CharField(max_length=20, choices=ARQUETIPOS)
    posicao_preferida = models.CharField(max_length=2, choices=POSICOES_TATICAS)
    clube_atual = models.ForeignKey(Clube, on_delete=models.SET_NULL, null=True, blank=True, related_name='elenco_jogadores')
    
    # Status
    descricao_lesao = models.CharField(max_length=255, null=True, blank=True)
    pontos_acao_diarios = models.IntegerField(default=1) # ESSENCIAL para a lógica de treino
    
    # Evolução
    temporada_nascimento = models.IntegerField()
    idade_inicial = models.IntegerField(default=17)
    teto_potencial_oculto = models.IntegerField(default=75)
    xp_disponivel = models.IntegerField(default=0)

    # Atributos
    fisico = models.IntegerField(default=60)
    tecnica = models.IntegerField(default=60)
    inteligencia = models.IntegerField(default=60)
    moral = models.IntegerField(default=100)
    media_fama = models.IntegerField(default=20)

    # Status
    seta_momento = models.IntegerField(default=0)
    lesionado_rodadas_restantes = models.IntegerField(default=0)
    rodadas_suspensao = models.IntegerField(default=0)

    # Economia
    saldo_bancario = models.BigIntegerField(default=0)
    salario_rodada = models.IntegerField(default=1000)
    
    @property
    def idade_atual(self):
        config = ServidorConfig.objects.first()
        return self.idade_inicial + (config.temporada_atual - self.temporada_nascimento)

    @property
    def ovr_calculado(self):
        base = (self.tecnica * 0.45) + (self.inteligencia * 0.35) + (self.fisico * 0.20)
        contrato_ativo = self.patrocinios.filter(ativo=True).first()
        if contrato_ativo:
            base += (contrato_ativo.marca.bonus_tecnica + contrato_ativo.marca.bonus_fisico) / 2
        return min(int(base) + self.seta_momento, 99)

    def __str__(self):
        return f"{self.nome_camisa} ({self.ovr_calculado})"
    
class EscalacaoPosicao(models.Model):
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='posicoes_taticas')
    posicao_campo = models.CharField(max_length=2, choices=Avatar.POSICOES_TATICAS)
    jogador_titular = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True, related_name='vaga_titular')
    bot_nome = models.CharField(max_length=50, default="Jogador Genérico")
    bot_ovr = models.IntegerField(default=60)

    class Meta:
        unique_together = ('clube', 'posicao_campo')

class PartidaMundo(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    clube_casa = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='jogos_casa')
    clube_fora = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='jogos_fora')
    gols_casa = models.IntegerField(default=0)
    gols_fora = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='agendada')
    minuto_atual = models.IntegerField(default=0)
    log_narracao = models.JSONField(default=list) 
    frases_narracao_ia = models.JSONField(default=list, blank=True)
    jogador_esperado = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True, related_name='lances_pendentes')
    opcoes_lance = models.JSONField(null=True, blank=True)
    vencimento_lance = models.DateTimeField(null=True, blank=True)

    def adicionar_log(self, texto, destaque=False):
        log = self.log_narracao
        log.append({'minuto': self.minuto_atual, 'texto': texto, 'destaque': destaque})
        self.log_narracao = log
        self.save()

class EstatisticaJogadorContrato(models.Model):
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='historico_estatisticas')
    temporada = models.IntegerField()
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)
    gols = models.IntegerField(default=0)
    soma_ratings_partida = models.FloatField(default=0.0)

class PropostaJanela(models.Model):
    STATUS_CHOICES = [('analise', 'Aguardando'), ('concluida', 'Concluída'), ('vetada_jogador', 'Vetada')]
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='ofertas_mercado')
    clube_comprador = models.ForeignKey(Clube, on_delete=models.CASCADE)
    valor_transferencia = models.BigIntegerField()
    salario_proposto = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='analise')

class ConflitoVestiario(models.Model):
    atleta_ofensor = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='conflitos_causados')
    atleta_ofendido = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='conflitos_sofridos')
    descricao_fato = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

class ConvocacaoSelecao(models.Model):
    temporada = models.IntegerField()
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE)
    pontuacao_ranking_calculada = models.FloatField()

class RegistroHistoricoCampeao(models.Model):
    temporada = models.IntegerField()
    campeonato_nome = models.CharField(max_length=100)
    clube_campeao_nome = models.CharField(max_length=100)
    clube_vice_nome = models.CharField(max_length=100)
    artilheiro_temporada_nome = models.CharField(max_length=100)
    artilheiro_gols_totais = models.IntegerField()
    mvp_temporada_nome = models.CharField(max_length=100)
    mvp_nota_media_final = models.FloatField()
    snapshot_elenco_selecao = models.JSONField()

class NoticiaJornal(models.Model):
    temporada = models.IntegerField(default=1)
    manchete = models.CharField(max_length=200)
    corpo_texto = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)

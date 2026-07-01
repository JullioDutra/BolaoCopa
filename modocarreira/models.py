from django.db import models
from django.contrib.auth.models import User


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
    escudo = models.ImageField(upload_to='escudos_carreira/', null=True, blank=True)
    orcamento = models.BigIntegerField(default=500000)
    prestigio_reputacao = models.IntegerField(default=50) # Escala de 1 a 100

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
        ordering = ['-pontos', '-vitorias', '(gols_pro-gols_contra)', '-gols_pro']

class MarcaPatrocinadora(models.Model):
    """ Marcas esportivas do ecossistema que oferecem contratos aos atletas """
    nome = models.CharField(max_length=50)
    reputacao_minima_exigida = models.IntegerField(default=20)
    
    # Modificadores de Atributo (Buffs da Chuteira/Equipamento)
    bonus_tecnica = models.IntegerField(default=0)
    bonus_fisico = models.IntegerField(default=0)
    reducao_risco_lesao = models.IntegerField(default=0) # Porcentagem de redução

    def __str__(self):
        return self.nome

class PatrocinioContrato(models.Model):
    """ Relacionamento de exclusividade comercial entre atleta e marca """
    avatar = models.ForeignKey('Avatar', on_delete=models.CASCADE, related_name='patrocinios')
    marca = models.ForeignKey(MarcaPatrocinadora, on_delete=models.CASCADE)
    valor_por_rodada = models.IntegerField()
    temporada_inicio = models.IntegerField()
    duracao_temporadas = models.IntegerField()
    ativo = models.BooleanField(default=True)

class Avatar(models.Model):
    """ Entidade mestre do jogador no metaverso """
    ARQUETIPOS = [
        ('xerife', 'Zagueiro Xerife'),
        ('maestro', 'Meia Maestro'),
        ('matador', 'Atacante Matador'),
        ('motorzinho', 'Ponta Ligeiro'),
    ]
    POSICOES_TATICAS = [
        ('GK', 'Goleiro'), ('CB', 'Zagueiro'), ('LB', 'Lateral Esquerdo'), ('RB', 'Lateral Direito'),
        ('DM', 'Volante'), ('CM', 'Meia Central'), ('AM', 'Meia Armador'),
        ('LW', 'Ponta Esquerda'), ('RW', 'Ponta Direita'), ('ST', 'Centroavante')
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='avatar_carreira')
    nome_camisa = models.CharField(max_length=20)
    arquetipo = models.CharField(max_length=20, choices=ARQUETIPOS)
    posicao_preferida = models.CharField(max_length=2, choices=POSICOES_TATICAS)
    clube_atual = models.ForeignKey(Clube, on_delete=models.SET_NULL, null=True, blank=True, related_name='elenco_jogadores')
    # Dentro da classe Avatar, por baixo do lesionado_rodadas_restantes:
    descricao_lesao = models.CharField(max_length=255, null=True, blank=True)
    
    # Controle de Evolução (Teto Dinâmico)
    temporada_nascimento = models.IntegerField()
    idade_inicial = models.IntegerField(default=17)
    teto_potencial_oculto = models.IntegerField(default=75) # Modificado por comportamento/desempenho
    xp_disponivel = models.IntegerField(default=0)

    # Pilares de Atributos Base
    fisico = models.IntegerField(default=60)
    tecnica = models.IntegerField(default=60)
    inteligencia = models.IntegerField(default=60)
    moral = models.IntegerField(default=100)
    media_fama = models.IntegerField(default=20)

    # Status Clínico e Disciplinar
    seta_momento = models.IntegerField(default=0) # Buffs/Debuffs de humor (-3 a +3)
    lesionado_rodadas_restantes = models.IntegerField(default=0)
    suspenso_competicao_id = models.ForeignKey(Campeonato, on_delete=models.SET_NULL, null=True, blank=True)
    rodadas_suspensao = models.IntegerField(default=0)

    # Economia
    saldo_bancario = models.BigIntegerField(default=0)
    salario_rodada = models.IntegerField(default=1000)
    clausula_rescisoria = models.BigIntegerField(default=50000)
    fim_contrato_temporada = models.IntegerField(default=1)
    bloqueado_para_venda = models.BooleanField(default=False) # Opção de veto do jogador

    @property
    def idade_atual(self):
        config = ServidorConfig.objects.first()
        return self.idade_inicial + (config.temporada_atual - self.temporada_nascimento)

    @property
    def ovr_calculado(self):
        # Média ponderada integrada com buffs de momento e equipamentos
        base = (self.tecnica * 0.45) + (self.inteligencia * 0.35) + (self.fisico * 0.20)
        
        # Injeta bônus de patrocínio ativo
        contrato_ativo = self.patrocinios.filter(ativo=True).first()
        if contrato_ativo:
            base += (contrato_ativo.marca.bonus_tecnica + contrato_ativo.marca.bonus_fisico) / 2
            
        return min(int(base) + self.seta_momento, 99)

    def __str__(self):
        return f"{self.nome_camisa} ({self.ovr_calculado})"
    
class EscalacaoPosicao(models.Model):
    """ Prancheta tática estruturada do clube para a rodada """
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='posicoes_taticas')
    posicao_campo = models.CharField(max_length=2, choices=Avatar.POSICOES_TATICAS)
    
    # Jogadores alocados (Se ambos nulos, a Engine roda um Bot genérico padrão)
    jogador_titular = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True, related_name='vaga_titular')
    jogador_reserva = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True, related_name='vaga_reserva')

    # Dados do Jogador Genérico (Bot caso a vaga real esteja desocupada)
    bot_nome = models.CharField(max_length=50, default="Jogador Genérico")
    bot_ovr = models.IntegerField(default=60)

    class Meta:
        unique_together = ('clube', 'posicao_campo')
        verbose_name = "Posição na Prancheta"
        verbose_name_plural = "Posições na Prancheta"

class PartidaMundo(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    clube_casa = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='jogos_casa')
    clube_fora = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='jogos_fora')
    
    # Placar
    gols_casa = models.IntegerField(default=0)
    gols_fora = models.IntegerField(default=0)
    
    # Controle de Estado Ao Vivo
    status = models.CharField(max_length=20, default='agendada') # agendada, andamento, finalizada
    minuto_atual = models.IntegerField(default=0)
    
    # O "Console" do Narrador
    log_narracao = models.JSONField(default=list) 
    
    # Controle de Ação Interativa (O lance chave)
    jogador_esperado = models.ForeignKey(Avatar, on_delete=models.SET_NULL, null=True, blank=True, related_name='lances_pendentes')
    opcoes_lance = models.JSONField(null=True, blank=True)
    vencimento_lance = models.DateTimeField(null=True, blank=True)
    # Dentro da classe PartidaMundo:
    frases_narracao_ia = models.JSONField(default=list, blank=True)

    def adicionar_log(self, texto, destaque=False):
        """ Adiciona uma linha de texto à narração da partida """
        log = self.log_narracao
        log.append({'minuto': self.minuto_atual, 'texto': texto, 'destaque': destaque})
        self.log_narracao = log
        self.save()

class EstatisticaJogadorContrato(models.Model):
    """ Histórico detalhado de desempenho por temporada de cada atleta """
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='historico_estatisticas')
    temporada = models.IntegerField()
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)

    jogos_titular = models.IntegerField(default=0)
    jogos_reserva = models.IntegerField(default=0)
    gols = models.IntegerField(default=0)
    assistencias = models.IntegerField(default=0)
    
    # Disciplina (Impacta diretamente suspensões)
    cartoes_amarelos = models.IntegerField(default=0)
    cartoes_vermelhos = models.IntegerField(default=0)
    
    # Avaliação de Nota
    soma_ratings_partida = models.FloatField(default=0.0)
    premios_mvp = models.IntegerField(default=0)

    @property
    def nota_media(self):
        total_jogos = self.jogos_titular + self.jogos_reserva
        if total_jogos == 0: return 0.0
        return round(self.soma_ratings_partida / total_jogos, 2)
    

class PropostaJanela(models.Model):
    """ Processamento de transferências realistas baseadas em orçamento e OVR """
    STATUS_CHOICES = [
        ('analise', 'Aguardando Avaliação'),
        ('recusada_clube', 'Recusada pelo Clube Detentor'),
        ('vetada_jogador', 'Vetada pelo Atleta'),
        ('concluida', 'Transferência Concluída')
    ]
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='ofertas_mercado')
    clube_comprador = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='propostas_enviadas')
    clube_vendedor = models.ForeignKey(Clube, on_delete=models.CASCADE, related_name='propostas_recebidas', null=True, blank=True)
    valor_transferencia = models.BigIntegerField()
    salario_proposto = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='analise')

class ConflitoVestiario(models.Model):
    """ Atritos gerados por decisões egoístas que causam debuff no entrosamento """
    atleta_ofensor = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='conflitos_causados')
    atleta_ofendido = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='conflitos_sofridos')
    descricao_fato = models.CharField(max_length=255)
    ativo = models.BooleanField(default=True)

class ConvocacaoSelecao(models.Model):
    """ Registro oficial dos atletas convocados para as seleções do servidor """
    temporada = models.IntegerField()
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='convocacoes_internacionais')
    pontuacao_ranking_calculada = models.FloatField() # Armzena o cálculo final (OVR + Estatísticas ponderadas por Divisão)

class RegistroHistoricoCampeao(models.Model):
    """ Arquivo consolidado para busca rápida no Museu Histórico """
    temporada = models.IntegerField()
    campeonato_nome = models.CharField(max_length=100)
    
    # Dados de Clubes e Atletas persistidos em string/JSON para proteger dados históricos contra deleções futuras
    clube_campeao_nome = models.CharField(max_length=100)
    clube_vice_nome = models.CharField(max_length=100)
    
    artilheiro_temporada_nome = models.CharField(max_length=100)
    artilheiro_gols_totais = models.IntegerField()
    
    mvp_temporada_nome = models.CharField(max_length=100)
    mvp_nota_media_final = models.FloatField()
    
    snapshot_elenco_selecao = models.JSONField(help_text="Lista estática dos atletas da seleção para consulta perpétua")

    def __str__(self):
        return f"Histórico {self.campeonato_nome} - Temporada {self.temporada}"

class NoticiaJornal(models.Model):
    temporada = models.IntegerField(default=1)
    manchete = models.CharField(max_length=200)
    corpo_texto = models.TextField()
    data_publicacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.manchete

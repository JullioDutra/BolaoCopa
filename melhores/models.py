from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Todo candidato começa com um quarto de "voto" para nunca ter odd infinita.
SUAVIZACAO = Decimal('0.25')


class Edicao(models.Model):
    """ Uma edição anual dos Melhores do Ano (ex.: 2026). """
    ano = models.IntegerField(unique=True)
    titulo = models.CharField(max_length=120, default="Melhores do Ano")
    ativa = models.BooleanField(default=True, help_text="Só a edição ativa aparece para os jogadores.")
    apostas_ate = models.DateTimeField(
        null=True, blank=True,
        help_text="Prazo geral das apostas. Vazio = apostas abertas até a staff fechar cada categoria.",
    )
    margem_casa = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('0.12'),
        help_text="Margem aplicada às odds (0.12 = 12%). Quanto maior, menores as odds.",
    )
    coins_por_voto = models.PositiveIntegerField(
        default=200,
        help_text="A cada X coins apostados em um candidato, ele ganha 1 'voto' virtual e a odd cai. "
                  "Menor = odds mais sensíveis ao movimento da galera.",
    )
    peso_anos_anteriores = models.DecimalField(
        max_digits=3, decimal_places=2, default=Decimal('0.25'),
        help_text="Peso de cada voto de anos antes do último (o último ano vale 1.00).",
    )

    class Meta:
        verbose_name = "Edição"
        verbose_name_plural = "Edições"
        ordering = ['-ano']

    def __str__(self):
        return f"{self.titulo} {self.ano}"

    @property
    def prazo_encerrado(self):
        return bool(self.apostas_ate and timezone.now() >= self.apostas_ate)


class Categoria(models.Model):
    TIPOS = [
        ('pessoa', 'Pessoa'),
        ('autor', 'Autor da frase/lance'),
        ('nome', 'Nome do grupo'),
    ]

    edicao = models.ForeignKey(Edicao, on_delete=models.CASCADE, related_name='categorias')
    slug = models.SlugField(max_length=60)
    nome = models.CharField(max_length=120)
    emoji = models.CharField(max_length=8, default='🏆')
    descricao = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=10, choices=TIPOS, default='pessoa')
    ordem = models.PositiveIntegerField(default=0)
    aberta = models.BooleanField(default=True, help_text="Desmarque para travar as apostas desta categoria.")
    vencedor = models.ForeignKey(
        'Candidato', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
    )
    liquidada = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordem', 'id']
        unique_together = [('edicao', 'slug')]

    def __str__(self):
        return f"{self.emoji} {self.nome} ({self.edicao.ano})"

    @property
    def aceita_apostas(self):
        return self.aberta and not self.liquidada and not self.edicao.prazo_encerrado and self.edicao.ativa


class Candidato(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='candidatos')
    nome = models.CharField(max_length=120)
    texto = models.CharField(
        max_length=300, blank=True,
        help_text="Opcional: a frase/lance específico (quando a categoria é de pérolas, micos etc.).",
    )
    votos_ano_anterior = models.PositiveIntegerField(default=0, help_text="Votos na última edição.")
    votos_anos_anteriores = models.PositiveIntegerField(default=0, help_text="Votos em edições mais antigas.")

    class Meta:
        ordering = ['-votos_ano_anterior', 'nome']
        unique_together = [('categoria', 'nome', 'texto')]

    def __str__(self):
        return f"{self.nome} — {self.categoria.nome}"

    @property
    def peso_historico(self):
        """ Peso base da odd: votos recentes + votos antigos (com desconto) + suavização. """
        edicao = self.categoria.edicao
        return (
            Decimal(self.votos_ano_anterior)
            + Decimal(self.votos_anos_anteriores) * edicao.peso_anos_anteriores
            + SUAVIZACAO
        )


class Aposta(models.Model):
    STATUS = [
        ('aberta', 'Aberta'),
        ('ganha', 'Ganha'),
        ('perdida', 'Perdida'),
        ('anulada', 'Anulada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apostas_melhores')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='apostas')
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='apostas')
    valor = models.PositiveIntegerField()
    odd_travada = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default='aberta')
    retorno = models.PositiveIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        # Uma aposta por categoria: trocar de candidato devolve o valor antigo e cria outra.
        unique_together = [('usuario', 'categoria')]
        ordering = ['-atualizada_em']

    def __str__(self):
        return f"{self.usuario.username}: {self.valor} em {self.candidato.nome} @ {self.odd_travada}"

    @property
    def retorno_potencial(self):
        return int(Decimal(self.valor) * self.odd_travada)


class Multipla(models.Model):
    """
    Aposta múltipla (acumulada): várias seleções de categorias DIFERENTES num único bilhete.
    A odd total é o produto das odds travadas (limitada a ODD_TOTAL_MAX); só paga se TODAS acertarem.
    Seleção anulada (categoria cancelada) conta como odd 1,00.
    """
    STATUS = Aposta.STATUS
    ODD_TOTAL_MAX = Decimal('100.00')
    MIN_SELECOES = 2
    MAX_SELECOES = 8
    MAX_ABERTAS = 10

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='multiplas_melhores')
    edicao = models.ForeignKey(Edicao, on_delete=models.CASCADE, related_name='multiplas')
    valor = models.PositiveIntegerField()
    odd_total = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default='aberta')
    retorno = models.PositiveIntegerField(default=0)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criada_em']

    def __str__(self):
        return f"Múltipla de {self.usuario.username}: {self.valor} @ {self.odd_total}"

    @property
    def retorno_potencial(self):
        return int(Decimal(self.valor) * self.odd_total)


class MultiplaSelecao(models.Model):
    multipla = models.ForeignKey(Multipla, on_delete=models.CASCADE, related_name='selecoes')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='selecoes_multipla')
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='selecoes_multipla')
    odd_travada = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10, choices=Aposta.STATUS, default='aberta')

    class Meta:
        unique_together = [('multipla', 'categoria')]

    def __str__(self):
        return f"{self.candidato.nome} @ {self.odd_travada}"

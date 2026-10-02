from django.contrib.auth.models import User
from django.db import models

from accounts.temas import normalizar

from .posicoes import NOME_POSICAO, ORDEM_POSICAO, POSICOES


class Time(models.Model):
    """ Time de futebol para pesquisa e comparativos (vem de APIs, do banco interno ou de arquivo). """
    nome = models.CharField(max_length=120)
    nome_curto = models.CharField(max_length=60, blank=True)
    sigla = models.CharField(max_length=6, blank=True)
    pais = models.CharField(max_length=60, blank=True)
    liga = models.CharField(max_length=80, blank=True)
    cidade = models.CharField(max_length=80, blank=True)
    estadio = models.CharField(max_length=100, blank=True)
    fundacao = models.PositiveIntegerField(null=True, blank=True)
    escudo_url = models.URLField(max_length=300, blank=True)
    cor = models.CharField(max_length=7, blank=True, help_text="Hex, ex.: #C8102E")
    clube_local = models.ForeignKey('palpites.Clube', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
                                    help_text="Clube do Bolão equivalente (usa o escudo enviado no Admin)")
    fonte = models.CharField(max_length=20, blank=True)
    ids_externos = models.JSONField(default=dict, blank=True, help_text='Ex.: {"football-data": 1783}')
    busca = models.CharField(max_length=400, blank=True, editable=False, db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        constraints = [models.UniqueConstraint(fields=['nome', 'pais'], name='time_unico_por_pais')]

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        self.busca = normalizar(' '.join([self.nome, self.nome_curto, self.sigla, self.cidade]))
        super().save(*args, **kwargs)

    @property
    def nome_exibicao(self):
        return self.nome_curto or self.nome

    @property
    def escudo_src(self):
        """ Escudo enviado no Admin (se houver) tem prioridade sobre o da API. """
        if self.clube_local_id and self.clube_local.escudo:
            return self.clube_local.escudo.url
        from .escudos import escudo_url
        return escudo_url(self.nome) or self.escudo_url or None

    @property
    def cor_hex(self):
        if self.cor and len(self.cor) == 7:
            return self.cor
        return self.clube_local.cor_hexadecimal if self.clube_local_id else '#1b5e20'


class Atleta(models.Model):
    nome = models.CharField(max_length=120)
    time = models.ForeignKey(Time, null=True, blank=True, on_delete=models.SET_NULL, related_name='atletas')
    posicao = models.CharField(max_length=3, choices=POSICOES)
    detalhe = models.CharField(max_length=40, blank=True, help_text="Ex.: Zagueiro, Lateral-direito, Volante")
    numero = models.PositiveSmallIntegerField(null=True, blank=True)
    nascimento = models.DateField(null=True, blank=True)
    nacionalidade = models.CharField(max_length=60, blank=True)
    altura_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    foto_url = models.URLField(max_length=300, blank=True)
    foto = models.ImageField(upload_to='atletas/', blank=True, null=True)
    overall = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Nota geral 0-99 (opcional)")
    valor_mercado = models.BigIntegerField(null=True, blank=True, help_text="Em euros (opcional)")
    fonte = models.CharField(max_length=20, blank=True)
    ids_externos = models.JSONField(default=dict, blank=True)
    busca = models.CharField(max_length=300, blank=True, editable=False, db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time__nome', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.get_posicao_display()})"

    def save(self, *args, **kwargs):
        self.busca = normalizar(self.nome)
        super().save(*args, **kwargs)

    @property
    def foto_src(self):
        return self.foto.url if self.foto else (self.foto_url or None)

    @property
    def idade(self):
        if not self.nascimento:
            return None
        from django.utils import timezone
        hoje = timezone.localdate()
        return hoje.year - self.nascimento.year - ((hoje.month, hoje.day) < (self.nascimento.month, self.nascimento.day))

    @property
    def ordem(self):
        return ORDEM_POSICAO.get(self.posicao, 9)


# ---------------------------------------------------------------- Comparativo + votação dos 11

class Comparativo(models.Model):
    """
    Duelo entre dois times. O criador escolhe os 11 iniciais de cada lado e abre uma votação:
    a galera elege os 11 melhores entre os 22 (1 goleiro, 4 defensores, 3 meias e 3 atacantes).
    """
    FORMACAO = {'GOL': 1, 'DEF': 4, 'MEI': 3, 'ATA': 3}   # 4-3-3

    criador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparativos')
    titulo = models.CharField(max_length=120, blank=True)
    time_a = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='+')
    time_b = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='+')
    criado_em = models.DateTimeField(auto_now_add=True)
    encerra_em = models.DateTimeField(null=True, blank=True)
    encerrado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo or f"{self.time_a.nome_exibicao} x {self.time_b.nome_exibicao}"

    @property
    def aberto(self):
        from django.utils import timezone
        if self.encerrado:
            return False
        return not (self.encerra_em and timezone.now() >= self.encerra_em)


class Escalacao(models.Model):
    """ Um dos 22 iniciais do comparativo (11 de cada time). """
    comparativo = models.ForeignKey(Comparativo, on_delete=models.CASCADE, related_name='iniciais')
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE, related_name='+')
    lado = models.CharField(max_length=1, choices=[('A', 'Time A'), ('B', 'Time B')])

    class Meta:
        unique_together = [('comparativo', 'atleta')]


class Voto(models.Model):
    comparativo = models.ForeignKey(Comparativo, on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votos_comparativo')
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE, related_name='+')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('comparativo', 'usuario', 'atleta')]


class Escudo(models.Model):
    """
    Catálogo GLOBAL de escudos: um registro por clube, reaproveitado por todos os jogos
    (bolão, X1, draft, trunfo, carreira…). `chave` é o nome normalizado, então
    "Flamengo", "CR Flamengo" e "FLAMENGO" apontam para o mesmo escudo.
    """
    chave = models.CharField(max_length=120, unique=True, editable=False)
    nome = models.CharField(max_length=120)
    apelidos = models.CharField(max_length=300, blank=True, help_text="Outros nomes separados por vírgula")
    arquivo = models.ImageField(upload_to='escudos/global/', blank=True, null=True)
    url = models.URLField(max_length=300, blank=True, help_text="Usado quando não há arquivo enviado")
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        from .escudos import chave_time, limpar_cache
        self.chave = chave_time(self.nome)
        super().save(*args, **kwargs)
        limpar_cache()

    @property
    def src(self):
        return self.arquivo.url if self.arquivo else (self.url or None)

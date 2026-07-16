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
    nome = models.CharField(max_length=100)
    posicao = models.CharField(max_length=50, choices=POSICOES_CHOICES)
    clube_atual = models.CharField(max_length=100, blank=True, null=True)
    modalidade = models.CharField(max_length=10, choices=[('resenha', 'Resenha'), ('pago', 'Pago')], default='resenha')
    foto = models.ImageField(upload_to='jogadores/', blank=True, null=True)
    convocado_oficial = models.BooleanField(default=False, help_text="Marque se este jogador faz parte da seleção oficial (usado tanto na Copa quanto no Brasileirão).")
    pontos_obtidos = models.IntegerField(default=0, help_text="Pontos ganhos por acertar esse jogador.")

    def __str__(self):
        return f"{self.nome} ({self.posicao})"


# ==========================================
# MODO COPA (ENCERRADO) — mantido só como histórico
# ==========================================
class Convocacao(models.Model):
    """Convocação de 26 jogadores para a Copa. Esse modo está ENCERRADO.
    O model é mantido apenas para exibir o histórico/campeão no mural."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='selecao_copa')
    jogadores = models.ManyToManyField(Jogador, related_name='convocados_copa')
    data_atualizacao = models.DateTimeField(auto_now=True)
    pontuacao_total = models.IntegerField(default=0)

    def total_convocados(self):
        return self.jogadores.count()

    def __str__(self):
        return f"[COPA] Seleção de {self.usuario.username} ({self.total_convocados()}/26)"

    @classmethod
    def calcular_campeao(cls):
        """Retorna dict com o usuário que mais acertou jogadores na lista oficial da Copa."""
        oficiais = set(Jogador.objects.filter(convocado_oficial=True).values_list('id', flat=True))
        if not oficiais:
            return None

        melhor_usuario = None
        melhor_acertos = -1
        for conv in cls.objects.select_related('usuario').all():
            escolhidos = set(conv.jogadores.values_list('id', flat=True))
            acertos = len(oficiais.intersection(escolhidos))
            if acertos > melhor_acertos:
                melhor_acertos = acertos
                melhor_usuario = conv.usuario

        if melhor_usuario is None:
            return None

        return {
            'usuario': melhor_usuario,
            'acertos': melhor_acertos,
            'total_oficiais': len(oficiais),
        }


# ==========================================
# NOVO MODO: SELEÇÃO DO BRASILEIRÃO (4-3-3)
# ==========================================

# Pontuação por jogador correto (assumida — ajuste se quiser outro valor).
PONTOS_JOGADOR_NA_SELECAO_OFICIAL = 10


class SelecaoBrasileirao(models.Model):
    """Escalação 4-3-3 (11 jogadores fixos por posição) para o modo Brasileirão."""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='selecao_brasileirao')

    goleiro = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Goleiro'})
    defensor_1 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Defensor'})
    defensor_2 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Defensor'})
    defensor_3 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Defensor'})
    defensor_4 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Defensor'})
    meia_1 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Meio-campista'})
    meia_2 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Meio-campista'})
    meia_3 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Meio-campista'})
    atacante_1 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Atacante'})
    atacante_2 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Atacante'})
    atacante_3 = models.ForeignKey(Jogador, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', limit_choices_to={'posicao': 'Atacante'})

    pontuacao_total = models.IntegerField(default=0)
    data_atualizacao = models.DateTimeField(auto_now=True)

    CAMPOS_ESCALACAO = [
        'goleiro', 'defensor_1', 'defensor_2', 'defensor_3', 'defensor_4',
        'meia_1', 'meia_2', 'meia_3', 'atacante_1', 'atacante_2', 'atacante_3',
    ]

    def jogadores_escalados(self):
        return [getattr(self, campo) for campo in self.CAMPOS_ESCALACAO if getattr(self, campo) is not None]

    def calcular_pontuacao(self):
        """Soma pontos para cada jogador escalado que estiver marcado como oficial."""
        pontos = 0
        for jogador in self.jogadores_escalados():
            if jogador.convocado_oficial:
                pontos += PONTOS_JOGADOR_NA_SELECAO_OFICIAL
        self.pontuacao_total = pontos
        self.save(update_fields=['pontuacao_total'])
        return pontos

    def __str__(self):
        return f"[BRASILEIRÃO 4-3-3] Seleção de {self.usuario.username} ({self.pontuacao_total} pts)"

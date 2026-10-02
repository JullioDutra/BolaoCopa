from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.dispatch import receiver
from django.db.models.signals import post_save
#from palpites.models import Clube

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Carteira.objects.create(usuario=instance)

class Carteira(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carteira')
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Carteira de {self.usuario.username} - Saldo: R$ {self.saldo}"

class Transacao(models.Model):
    TIPO_CHOICES = [
        ('deposito', 'Depósito (Pix)'),
        ('aposta', 'Participação Bolão/Convocação'),
        ('premio', 'Premiação Recebida'),
        ('saque', 'Retirada de Saldo'),
    ]
    
    carteira = models.ForeignKey(Carteira, on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)
    descricao = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} ({self.carteira.usuario.username})"


class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    time_coracao = models.ForeignKey('palpites.Clube', on_delete=models.SET_NULL, null=True, blank=True)
    viu_efeito_hoje = models.BooleanField(default=False) 

    # Tema do site: se True, o visual segue as cores do time do coração
    usar_tema_do_time = models.BooleanField(default=True)

    # Retenção: sequência de dias seguidos acessando o app
    streak_dias = models.PositiveIntegerField(default=0)
    maior_streak = models.PositiveIntegerField(default=0)
    ultimo_acesso_dia = models.DateField(null=True, blank=True)

    # Perfil editável
    telefone = models.CharField(max_length=20, blank=True, help_text="WhatsApp só com dígitos, com DDI (55...)")
    avatar = models.CharField(max_length=8, default='⚽')
    frase = models.CharField(max_length=80, blank=True, help_text="Frase de torcedor mostrada no seu cartão")
    avisos_whatsapp = models.BooleanField(default=True, help_text="Permite que a staff chame você pelo WhatsApp")

    # Recuperação de senha por dados do participante
    PERGUNTAS_SECRETAS = [
        ('craque', 'Quem é o maior craque que você já viu jogar?'),
        ('estadio', 'Qual foi o primeiro estádio que você foi?'),
        ('gol', 'Qual foi o gol mais marcante da sua vida?'),
        ('apelido', 'Qual era seu apelido de infância?'),
        ('pet', 'Qual o nome do seu primeiro bicho de estimação?'),
    ]
    pergunta_secreta = models.CharField(max_length=10, choices=PERGUNTAS_SECRETAS, blank=True)
    resposta_secreta_hash = models.CharField(max_length=128, blank=True)
    bonus_perfil_pago = models.BooleanField(default=False)

    @property
    def perfil_completo(self):
        return bool(self.telefone and self.resposta_secreta_hash)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class CarteiraCoins(models.Model):
    """
    Moeda virtual do app (NÃO é dinheiro real, não tem relação com a Carteira em R$).
    Usada nas brincadeiras do grupo: apostas dos Melhores do Ano, bônus diário, etc.
    """
    SALDO_INICIAL = 1000

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carteira_coins')
    saldo = models.IntegerField(default=SALDO_INICIAL)

    def __str__(self):
        return f"{self.usuario.username}: {self.saldo} Cartola Coins"


class MovimentoCoins(models.Model):
    """ Extrato da CarteiraCoins (toda entrada/saída fica registrada). """
    carteira = models.ForeignKey(CarteiraCoins, on_delete=models.CASCADE, related_name='movimentos')
    valor = models.IntegerField(help_text="Positivo = entrada, negativo = saída")
    motivo = models.CharField(max_length=255)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-id']

    def __str__(self):
        return f"{self.carteira.usuario.username} {self.valor:+d} ({self.motivo})"

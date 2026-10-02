"""
Sequência diária de acessos ("streak") com bônus em Cartola Coins.

Quanto mais dias seguidos, maior o bônus. No 7º dia seguido há um prêmio extra
e o ciclo de bônus recomeça a escalar (a sequência em si continua contando).
"""
from datetime import timedelta

from django.utils import timezone

from . import coins
from .models import PerfilUsuario

BONUS_BASE = 25
BONUS_POR_DIA = 15
BONUS_MAXIMO = 100
BONUS_SEMANA_PERFEITA = 200


def bonus_do_dia(streak):
    """ Bônus de um dia da sequência (streak >= 1). """
    bonus = min(BONUS_BASE + BONUS_POR_DIA * (streak - 1), BONUS_MAXIMO)
    if streak % 7 == 0:
        bonus += BONUS_SEMANA_PERFEITA
    return bonus


def registrar_acesso(usuario, hoje=None):
    """
    Registra o acesso do dia. Devolve um dict com o resultado quando houve bônus
    novo, ou None se o usuário já tinha coletado hoje.
    """
    hoje = hoje or timezone.localdate()
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)

    if perfil.ultimo_acesso_dia == hoje:
        return None

    if perfil.ultimo_acesso_dia == hoje - timedelta(days=1):
        perfil.streak_dias += 1
    else:
        perfil.streak_dias = 1
    perfil.maior_streak = max(perfil.maior_streak, perfil.streak_dias)
    perfil.ultimo_acesso_dia = hoje
    perfil.save(update_fields=['streak_dias', 'maior_streak', 'ultimo_acesso_dia'])

    bonus = bonus_do_dia(perfil.streak_dias)
    coins.creditar(usuario, bonus, f"🔥 Bônus diário (sequência de {perfil.streak_dias} dia(s))")
    return {
        'streak': perfil.streak_dias,
        'bonus': bonus,
        'semana_perfeita': perfil.streak_dias % 7 == 0,
        'proximo_bonus': bonus_do_dia(perfil.streak_dias + 1),
    }

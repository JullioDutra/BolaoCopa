"""
Operações da moeda virtual "Cartola Coins".

Toda alteração de saldo passa por aqui para (1) ficar registrada no extrato
(MovimentoCoins) e (2) nunca deixar o saldo ficar negativo.
"""
from django.db import transaction

from .models import CarteiraCoins, MovimentoCoins, PerfilUsuario


class SaldoInsuficiente(Exception):
    pass


def obter_carteira(usuario):
    """ Devolve a carteira de coins do usuário; na 1ª vez cria com o saldo inicial (1000). """
    carteira, criada = CarteiraCoins.objects.get_or_create(usuario=usuario)
    if criada:
        MovimentoCoins.objects.create(
            carteira=carteira,
            valor=CarteiraCoins.SALDO_INICIAL,
            motivo="🎁 Bônus de boas-vindas",
        )
    return carteira


def saldo(usuario):
    return obter_carteira(usuario).saldo


@transaction.atomic
def creditar(usuario, valor, motivo):
    valor = int(valor)
    if valor <= 0:
        raise ValueError("O valor a creditar deve ser positivo.")
    carteira = CarteiraCoins.objects.select_for_update().get(pk=obter_carteira(usuario).pk)
    carteira.saldo += valor
    carteira.save(update_fields=['saldo'])
    MovimentoCoins.objects.create(carteira=carteira, valor=valor, motivo=motivo)
    return carteira.saldo


@transaction.atomic
def debitar(usuario, valor, motivo):
    valor = int(valor)
    if valor <= 0:
        raise ValueError("O valor a debitar deve ser positivo.")
    carteira = CarteiraCoins.objects.select_for_update().get(pk=obter_carteira(usuario).pk)
    if carteira.saldo < valor:
        raise SaldoInsuficiente(f"Saldo insuficiente: você tem {carteira.saldo} e precisa de {valor}.")
    carteira.saldo -= valor
    carteira.save(update_fields=['saldo'])
    MovimentoCoins.objects.create(carteira=carteira, valor=-valor, motivo=motivo)
    return carteira.saldo


def obter_perfil(usuario):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=usuario)
    return perfil

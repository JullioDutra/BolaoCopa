from decimal import Decimal
from django.db import transaction
from accounts.models import Transacao

def debitar_participacao(usuario, descricao_bolao):
    CUSTO = Decimal('10.00')
    carteira = usuario.carteira

    if carteira.saldo >= CUSTO:
        with transaction.atomic():
            carteira.saldo -= CUSTO
            carteira.save()
            
            # Registra a transação para o usuário ver o extrato depois
            Transacao.objects.create(
                carteira=carteira,
                tipo='aposta',
                valor=CUSTO,
                descricao=f"Participação: {descricao_bolao}"
            )
        return True
    return False # Saldo insuficiente
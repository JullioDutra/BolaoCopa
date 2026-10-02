from django.db import transaction
from django.db.models import Sum

from accounts import coins
from accounts.models import CarteiraCoins

from .models import Aposta, Candidato, Categoria
from .odds import calcular_odds

APOSTA_MINIMA = 10


class ApostaInvalida(Exception):
    """ Erro de regra de negócio com mensagem pronta para mostrar ao usuário. """


@transaction.atomic
def apostar(usuario, categoria_id, candidato_id, valor):
    """
    Cria ou troca a aposta do usuário em uma categoria.

    Se já havia uma aposta aberta, o valor antigo é devolvido antes de debitar o
    novo, e a odd é recalculada SEM o valor antigo (para não se auto-influenciar).
    """
    try:
        valor = int(valor)
    except (TypeError, ValueError):
        raise ApostaInvalida("Informe um valor válido para a aposta.")
    if valor < APOSTA_MINIMA:
        raise ApostaInvalida(f"A aposta mínima é de {APOSTA_MINIMA} Cartola Coins.")

    categoria = Categoria.objects.select_for_update().select_related('edicao').filter(pk=categoria_id).first()
    if categoria is None:
        raise ApostaInvalida("Categoria não encontrada.")
    if not categoria.aceita_apostas:
        raise ApostaInvalida("As apostas desta categoria estão encerradas.")

    candidato = Candidato.objects.filter(pk=candidato_id, categoria=categoria).first()
    if candidato is None:
        raise ApostaInvalida("Escolha um candidato da lista.")

    anterior = Aposta.objects.filter(usuario=usuario, categoria=categoria).first()
    if anterior is not None:
        if anterior.status != 'aberta':
            raise ApostaInvalida("Esta aposta já foi resolvida.")
        coins.creditar(usuario, anterior.valor, f"↩️ Aposta trocada: {categoria.nome}")
        anterior.delete()

    try:
        coins.debitar(usuario, valor, f"🎯 Aposta: {candidato.nome} em {categoria.nome}")
    except coins.SaldoInsuficiente as erro:
        raise ApostaInvalida(str(erro))

    odd = calcular_odds(categoria)[candidato.id]
    return Aposta.objects.create(
        usuario=usuario, categoria=categoria, candidato=candidato, valor=valor, odd_travada=odd,
    )


@transaction.atomic
def cancelar_aposta(usuario, categoria_id):
    categoria = Categoria.objects.select_related('edicao').filter(pk=categoria_id).first()
    aposta = Aposta.objects.filter(usuario=usuario, categoria_id=categoria_id, status='aberta').first()
    if categoria is None or aposta is None:
        raise ApostaInvalida("Você não tem aposta aberta nesta categoria.")
    if not categoria.aceita_apostas:
        raise ApostaInvalida("As apostas desta categoria estão encerradas.")
    coins.creditar(usuario, aposta.valor, f"↩️ Aposta cancelada: {categoria.nome}")
    aposta.delete()


@transaction.atomic
def liquidar(categoria_id, candidato_vencedor_id):
    """
    Define o vencedor da categoria e paga as apostas (valor × odd travada).
    Idempotente: liquidar duas vezes não paga duas vezes.
    """
    categoria = Categoria.objects.select_for_update().get(pk=categoria_id)
    if categoria.liquidada:
        raise ApostaInvalida("Esta categoria já foi liquidada.")
    vencedor = Candidato.objects.get(pk=candidato_vencedor_id, categoria=categoria)

    pagos = 0
    for aposta in categoria.apostas.select_related('usuario').filter(status='aberta'):
        if aposta.candidato_id == vencedor.id:
            aposta.status = 'ganha'
            aposta.retorno = aposta.retorno_potencial
            coins.creditar(aposta.usuario, aposta.retorno,
                           f"🏆 Aposta certa! {vencedor.nome} em {categoria.nome} (odd {aposta.odd_travada})")
            pagos += 1
        else:
            aposta.status = 'perdida'
            aposta.retorno = 0
        aposta.save(update_fields=['status', 'retorno', 'atualizada_em'])

    categoria.vencedor = vencedor
    categoria.liquidada = True
    categoria.aberta = False
    categoria.save(update_fields=['vencedor', 'liquidada', 'aberta'])
    return pagos


@transaction.atomic
def anular(categoria_id):
    """ Cancela a categoria e devolve o valor de todas as apostas abertas. """
    categoria = Categoria.objects.select_for_update().get(pk=categoria_id)
    if categoria.liquidada:
        raise ApostaInvalida("Esta categoria já foi liquidada.")
    for aposta in categoria.apostas.select_related('usuario').filter(status='aberta'):
        coins.creditar(aposta.usuario, aposta.valor, f"↩️ Categoria anulada: {categoria.nome}")
        aposta.status = 'anulada'
        aposta.save(update_fields=['status', 'atualizada_em'])
    categoria.aberta = False
    categoria.save(update_fields=['aberta'])


def ranking(edicao):
    """
    Ranking de patrimônio: saldo em coins + valor ainda em jogo nas apostas abertas.
    Só entra quem já abriu a carteira de coins.
    """
    em_jogo = dict(
        Aposta.objects.filter(categoria__edicao=edicao, status='aberta')
        .values_list('usuario_id').annotate(total=Sum('valor'))
    )
    linhas = []
    for carteira in CarteiraCoins.objects.select_related('usuario'):
        extra = em_jogo.get(carteira.usuario_id, 0)
        linhas.append({
            'usuario': carteira.usuario,
            'saldo': carteira.saldo,
            'em_jogo': extra,
            'patrimonio': carteira.saldo + extra,
        })
    linhas.sort(key=lambda l: l['patrimonio'], reverse=True)
    return linhas

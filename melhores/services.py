from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from accounts import coins
from accounts.models import CarteiraCoins

from .models import Aposta, Candidato, Categoria, Edicao, Multipla, MultiplaSelecao
from .odds import calcular_odds

APOSTA_MINIMA = 10


class ApostaInvalida(Exception):
    """ Erro de regra de negócio com mensagem pronta para mostrar ao usuário. """


class OddMudou(ApostaInvalida):
    """ A odd caiu entre a tela do usuário e a confirmação; ele precisa confirmar de novo. """


@transaction.atomic
def apostar(usuario, categoria_id, candidato_id, valor, odd_esperada=None):
    """
    Cria ou troca a aposta do usuário em uma categoria.

    `odd_esperada` (opcional) é a odd que o usuário viu na tela: se a odd atual for
    MENOR, a aposta é recusada (OddMudou) e nada é debitado; se for maior, vale a melhor.

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
    if odd_esperada is not None and odd < Decimal(str(odd_esperada)):
        # Levanta dentro do atomic: devolve/debita tudo de volta
        raise OddMudou(f"A odd de {candidato.nome} mudou de {odd_esperada} para {odd}. Confirme de novo.")
    aposta = Aposta.objects.create(
        usuario=usuario, categoria=categoria, candidato=candidato, valor=valor, odd_travada=odd,
    )
    _publicar_aposta(usuario, f"apostou 🪙 {valor} em {candidato.nome} ({categoria.nome}) @ {odd}")
    return aposta


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
            _publicar_aposta(aposta.usuario, f"acertou {vencedor.nome} em {categoria.nome} e levou 🪙 {aposta.retorno}")
            pagos += 1
        else:
            aposta.status = 'perdida'
            aposta.retorno = 0
        aposta.save(update_fields=['status', 'retorno', 'atualizada_em'])

    categoria.vencedor = vencedor
    categoria.liquidada = True
    categoria.aberta = False
    categoria.save(update_fields=['vencedor', 'liquidada', 'aberta'])
    _resolver_selecoes_multipla(categoria, vencedor)
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
    _resolver_selecoes_multipla(categoria, None)


def _publicar_aposta(usuario, texto):
    """ Feed + conquistas (só depois de a transação principal confirmar; falhas aqui nunca derrubam a aposta). """
    from avisos import atividade, conquistas
    from django.db import transaction as tx
    tx.on_commit(lambda: (atividade.registrar(usuario, 'aposta', f"🎟️ {atividade.nome_publico(usuario)} {texto}", '/melhores/'),
                          conquistas.checar(usuario)))


def ranking(edicao):
    """
    Ranking de patrimônio: saldo em coins + valor ainda em jogo nas apostas abertas.
    Só entra quem já abriu a carteira de coins.
    """
    em_jogo = dict(
        Aposta.objects.filter(categoria__edicao=edicao, status='aberta')
        .values_list('usuario_id').annotate(total=Sum('valor'))
    )
    for usuario_id, total in (Multipla.objects.filter(edicao=edicao, status='aberta')
                              .values_list('usuario_id').annotate(total=Sum('valor'))):
        em_jogo[usuario_id] = em_jogo.get(usuario_id, 0) + total
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



# ---------------------------------------------------------------- múltiplas

def odd_da_multipla(odds):
    """ Produto das odds, limitado ao teto. """
    total = Decimal(1)
    for odd in odds:
        total *= Decimal(odd)
    return min(total, Multipla.ODD_TOTAL_MAX).quantize(Decimal('0.01'))


@transaction.atomic
def apostar_multipla(usuario, edicao_id, selecoes, valor):
    """
    `selecoes` = [(categoria_id, candidato_id, odd_esperada_ou_None), ...].
    Falha inteira (nada é debitado) se alguma seleção for inválida ou a odd tiver caído.
    """
    try:
        valor = int(valor)
    except (TypeError, ValueError):
        raise ApostaInvalida("Informe um valor válido para a múltipla.")
    if valor < APOSTA_MINIMA:
        raise ApostaInvalida(f"A aposta mínima é de {APOSTA_MINIMA} Cartola Coins.")
    if not (Multipla.MIN_SELECOES <= len(selecoes) <= Multipla.MAX_SELECOES):
        raise ApostaInvalida(f"Uma múltipla precisa de {Multipla.MIN_SELECOES} a {Multipla.MAX_SELECOES} seleções.")
    categorias_ids = [int(c) for c, _, _ in selecoes]
    if len(set(categorias_ids)) != len(categorias_ids):
        raise ApostaInvalida("A múltipla aceita só uma seleção por categoria.")

    edicao = Edicao.objects.filter(pk=edicao_id, ativa=True).first()
    if edicao is None:
        raise ApostaInvalida("Edição não encontrada.")
    if Multipla.objects.filter(usuario=usuario, edicao=edicao, status='aberta').count() >= Multipla.MAX_ABERTAS:
        raise ApostaInvalida(f"Você já tem {Multipla.MAX_ABERTAS} múltiplas abertas.")

    linhas = []
    for categoria_id, candidato_id, odd_esperada in selecoes:
        categoria = Categoria.objects.select_related('edicao').filter(pk=categoria_id, edicao=edicao).first()
        if categoria is None or not categoria.aceita_apostas:
            raise ApostaInvalida("Uma das categorias da múltipla está fechada.")
        candidato = Candidato.objects.filter(pk=candidato_id, categoria=categoria).first()
        if candidato is None:
            raise ApostaInvalida("Escolha candidatos válidos.")
        odd = calcular_odds(categoria)[candidato.id]
        if odd_esperada is not None and odd < Decimal(str(odd_esperada)):
            raise OddMudou(f"A odd de {candidato.nome} mudou de {odd_esperada} para {odd}. Confirme de novo.")
        linhas.append((categoria, candidato, odd))

    try:
        coins.debitar(usuario, valor, f"🎟️ Múltipla de {len(linhas)} seleções")
    except coins.SaldoInsuficiente as erro:
        raise ApostaInvalida(str(erro))

    multipla = Multipla.objects.create(
        usuario=usuario, edicao=edicao, valor=valor, odd_total=odd_da_multipla(o for _, _, o in linhas),
    )
    for categoria, candidato, odd in linhas:
        MultiplaSelecao.objects.create(multipla=multipla, categoria=categoria, candidato=candidato, odd_travada=odd)
    _publicar_aposta(usuario, f"montou uma múltipla de {len(linhas)} seleções @ {multipla.odd_total} (🪙 {valor})")
    return multipla


def _resolver_selecoes_multipla(categoria, vencedor):
    """
    Chamado ao liquidar/anular uma categoria: fecha as seleções dela e, se der pra
    decidir, paga ou perde as múltiplas. Idempotente (só toca em múltiplas abertas).
    """
    for selecao in MultiplaSelecao.objects.filter(categoria=categoria, status='aberta', multipla__status='aberta'):
        if vencedor is None:
            selecao.status = 'anulada'
        else:
            selecao.status = 'ganha' if selecao.candidato_id == vencedor.id else 'perdida'
        selecao.save(update_fields=['status'])
        _recalcular_multipla(selecao.multipla)


def _recalcular_multipla(multipla):
    if multipla.status != 'aberta':
        return
    selecoes = list(multipla.selecoes.select_related('candidato'))
    if any(s.status == 'perdida' for s in selecoes):
        multipla.status, multipla.retorno = 'perdida', 0
    elif any(s.status == 'aberta' for s in selecoes):
        return                                     # ainda falta resultado
    elif all(s.status == 'anulada' for s in selecoes):
        multipla.status, multipla.retorno = 'anulada', multipla.valor
        coins.creditar(multipla.usuario, multipla.valor, "↩️ Múltipla anulada: valor devolvido")
    else:
        odd = odd_da_multipla(s.odd_travada for s in selecoes if s.status == 'ganha')   # anulada conta 1,00
        multipla.status, multipla.odd_total = 'ganha', odd
        multipla.retorno = int(Decimal(multipla.valor) * odd)
        coins.creditar(multipla.usuario, multipla.retorno, f"🏆 Múltipla vencedora (odd {odd})")
        _publicar_aposta(multipla.usuario, f"ACERTOU uma múltipla de {len(selecoes)} seleções e levou 🪙 {multipla.retorno}!")
    multipla.save(update_fields=['status', 'retorno', 'odd_total'])

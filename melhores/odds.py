"""
Motor de odds dos Melhores do Ano.

  peso do candidato = peso histórico (votos de 2025 + 0,25 × votos antigos + 0,5)
                    + coins apostados nele ÷ coins_por_voto (movimento da galera)

  probabilidade = peso ÷ soma dos pesos da categoria
  odd bruta     = (1 − margem) ÷ probabilidade
  odd           = 1 + (bruta − 1) × FATOR_COMPRESSAO, limitada entre ODD_MIN e ODD_MAX

Resultado: quem foi muito votado no passado paga pouco, os azarões pagam muito,
e quando a galera despeja coins em um nome a odd dele vai caindo ao vivo.
A odd é "travada" no momento da aposta, então apostar cedo em um azarão compensa.
"""
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Count, Sum

from .models import Aposta

ODD_MIN = Decimal('1.10')
ODD_MAX = Decimal('10.00')
# Comprime a distância até 1,00: odd = 1 + (odd_bruta - 1) × fator. Deixa favoritos e azarões mais baixos.
FATOR_COMPRESSAO = Decimal('0.60')
CENTAVOS = Decimal('0.01')


def calcular_odds(categoria):
    """
    Devolve {candidato_id: Decimal(odd)} para todos os candidatos da categoria,
    considerando as apostas ainda abertas.
    """
    edicao = categoria.edicao
    candidatos = list(categoria.candidatos.all())
    if not candidatos:
        return {}

    coins_por_candidato = dict(
        Aposta.objects.filter(categoria=categoria, status='aberta')
        .values_list('candidato_id').annotate(total=Sum('valor'))
    )

    pesos = {}
    for c in candidatos:
        movimento = Decimal(coins_por_candidato.get(c.id, 0)) / Decimal(max(edicao.coins_por_voto, 1))
        pesos[c.id] = c.peso_historico + movimento

    soma = sum(pesos.values())
    odds = {}
    for c in candidatos:
        prob = pesos[c.id] / soma
        bruta = (Decimal(1) - edicao.margem_casa) / prob
        odd = Decimal(1) + (bruta - 1) * FATOR_COMPRESSAO
        odd = min(max(odd, ODD_MIN), ODD_MAX)
        odds[c.id] = odd.quantize(CENTAVOS, rounding=ROUND_HALF_UP)
    return odds


def distribuicao_da_galera(categoria):
    """ {candidato_id: (coins, apostadores)} — usado no gráfico "pra quem a galera tá apostando". """
    linhas = (
        Aposta.objects.filter(categoria=categoria, status='aberta')
        .values('candidato_id').annotate(coins=Sum('valor'))
    )
    contagem = dict(
        Aposta.objects.filter(categoria=categoria, status='aberta')
        .values_list('candidato_id').annotate(n=Count('id'))
    )
    return {l['candidato_id']: (l['coins'], contagem.get(l['candidato_id'], 0)) for l in linhas}

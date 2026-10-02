"""
Scout: transforma números em veredito — "mitou" ou "bagre" — considerando a posição,
o tempo em campo e quanto o jogador custou/vale.

Nota 0–100:
  produção por 90 min (gols/assistências/defesa) ........ comparada com um "padrão de Série A" por posição
  nota média da temporada (se houver) ................... pesa mais que a produção
  cartões ................................................ descontam até 12 pontos
Veredito = nota + ajuste de custo-benefício (jogador caro que rende pouco é "bagre caro";
jogador barato que rende muito é "achado").
"""
import math
from decimal import Decimal

from .models import EstatisticaAtleta

MIN_MINUTOS = 270          # menos que isso não gera veredito (amostra pequena)
PADRAO_POR_90 = {'ATA': 0.60, 'MEI': 0.38, 'DEF': 0.12}
PADRAO_SEM_SOFRER = 0.30   # goleiro: 30% de jogos sem sofrer gol é um bom nível

FAIXAS = [
    (80, 'MITOU', '🐐', 'mitou'),
    (65, 'Boa contratação', '👏', 'boa'),
    (50, 'Cumpre o papel', '😐', 'ok'),
    (35, 'Decepciona', '😬', 'ruim'),
    (0, 'BAGRE', '🐟', 'bagre'),
]


def _faixa(nota):
    for minimo, rotulo, emoji, classe in FAIXAS:
        if nota >= minimo:
            return rotulo, emoji, classe


def _produz_por_90(est, posicao):
    f = 90 / max(est.minutos, 1)
    if posicao == 'GOL':
        if est.jogos <= 0:
            return 0.0, 'sem jogos'
        taxa = est.jogos_sem_sofrer / est.jogos
        return min(100, taxa / PADRAO_SEM_SOFRER * 70), f'{taxa * 100:.0f}% dos jogos sem sofrer gol'
    g, a = est.gols * f, est.assistencias * f
    if posicao == 'ATA':
        valor = g + a * 0.55
    elif posicao == 'MEI':
        valor = g * 0.9 + a * 0.8
    else:
        valor = g * 1.2 + a * 0.9 + (est.jogos_sem_sofrer / est.jogos * 0.05 if est.jogos else 0)
    nota = min(100, valor / PADRAO_POR_90.get(posicao, 0.3) * 70)
    return nota, f'{g + a:.2f} gols+assistências por 90 min'


def avaliar(est):
    """ Devolve um dict com nota, veredito, selo de custo-benefício e os motivos. """
    posicao = est.atleta.posicao
    resultado = {'estatistica': est, 'nota': None, 'veredito': 'Sem amostra', 'emoji': '🤷', 'classe': 'sem',
                 'selo': '', 'motivos': [], 'confianca': 'baixa'}
    if est.minutos < MIN_MINUTOS:
        resultado['motivos'].append(f'Só {est.minutos} min em campo (mínimo {MIN_MINUTOS}).')
        return resultado

    producao, texto = _produz_por_90(est, posicao)
    resultado['motivos'].append(texto)
    nota_media = float(est.nota_media) if est.nota_media else None
    if nota_media:
        nota_nota = max(0, min(100, (nota_media - 5.5) / 2.5 * 100))
        base = 0.6 * nota_nota + 0.4 * producao
        resultado['motivos'].append(f'nota média {nota_media:.2f}')
        resultado['confianca'] = 'alta'
    elif posicao in ('DEF', 'GOL'):
        base = 0.5 * producao + 25  # sem nota, defensor/goleiro não é medido só por gol
        resultado['confianca'] = 'media'
    else:
        base = producao
        resultado['confianca'] = 'alta' if est.minutos >= 900 else 'media'

    f = 90 / max(est.minutos, 1)
    cartoes = (est.amarelos + 3 * est.vermelhos) * f
    desconto = min(12, cartoes * 8)
    if desconto >= 3:
        resultado['motivos'].append(f'{est.amarelos} amarelo(s) e {est.vermelhos} vermelho(s)')
    nota = max(0, min(100, base - desconto))
    resultado['nota'] = round(nota)

    custo = (est.valor_contratacao or est.atleta.valor_mercado or 0) / 1_000_000
    esperado = 50 + min(25, 10 * math.log10(1 + custo)) if custo else 50
    rotulo, emoji, classe = _faixa(nota)
    if custo >= 5 and nota < esperado - 15:
        resultado['selo'] = '💸 Bagre caro'
        resultado['motivos'].append(f'custou/vale ~€{custo:.1f} mi e rende abaixo do esperado ({esperado:.0f})')
    elif custo and custo < 5 and nota >= esperado + 20:
        resultado['selo'] = '💎 Achado barato'
        resultado['motivos'].append(f'custo baixo (~€{custo:.1f} mi) para esse rendimento')
    resultado.update(veredito=rotulo, emoji=emoji, classe=classe)
    return resultado


def _consulta(temporada=None, competicao='', posicao='', contratados=False):
    qs = EstatisticaAtleta.objects.select_related('atleta', 'time')
    if temporada:
        qs = qs.filter(temporada=temporada)
    if competicao:
        qs = qs.filter(competicao=competicao)
    if posicao:
        qs = qs.filter(atleta__posicao=posicao)
    if contratados:
        qs = qs.filter(contratado=True)
    return qs


def ranking(temporada=None, competicao='', posicao='', contratados=False, limite=10):
    """ {'mitaram': [...], 'bagres': [...]} — só quem tem amostra suficiente. """
    avaliados = [a for a in map(avaliar, _consulta(temporada, competicao, posicao, contratados)) if a['nota'] is not None]
    avaliados.sort(key=lambda a: a['nota'], reverse=True)
    return {'mitaram': avaliados[:limite],
            'bagres': sorted(avaliados, key=lambda a: a['nota'])[:limite],
            'total': len(avaliados)}


def balanco_time(time, temporada=None):
    """ Como o time se saiu nas contratações (ou no elenco todo, se não houver marcação). """
    lista = [a for a in map(avaliar, _consulta(temporada).filter(time=time)) if a['nota'] is not None]
    chegadas = [a for a in lista if a['estatistica'].contratado]
    base = chegadas or lista
    if not base:
        return None
    media = sum(a['nota'] for a in base) / len(base)
    rotulo, emoji, classe = _faixa(media)
    return {
        'media': round(media), 'veredito': 'MITOU nas contratações' if media >= 70 and chegadas else rotulo,
        'emoji': emoji, 'classe': classe, 'so_contratacoes': bool(chegadas), 'total': len(base),
        'melhor': max(base, key=lambda a: a['nota']), 'pior': min(base, key=lambda a: a['nota']),
        'jogadores': sorted(base, key=lambda a: -a['nota']),
    }


def temporadas_disponiveis():
    return list(EstatisticaAtleta.objects.order_by('-temporada').values_list('temporada', flat=True).distinct())


def decimal_ou_none(valor):
    try:
        return Decimal(str(valor).replace(',', '.')) if valor not in (None, '') else None
    except Exception:
        return None

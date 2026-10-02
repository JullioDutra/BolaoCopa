"""Regras do Comparativo de times e da votação "os 11 melhores"."""
from collections import Counter

from django.db import transaction
from django.utils import timezone

from accounts import coins

from .models import Atleta, Comparativo, Escalacao, Voto
from .posicoes import ORDEM_POSICAO

FORMACAO = Comparativo.FORMACAO            # {'GOL': 1, 'DEF': 4, 'MEI': 3, 'ATA': 3}
RECOMPENSA_VOTO = 10


class ComparativoInvalido(Exception):
    """ Erro de regra com mensagem pronta para o usuário. """


def sugerir_titulares(time):
    """ Os 11 iniciais sugeridos (4-3-3): melhores por overall; sem overall, ordem do cadastro. """
    atletas = list(time.atletas.all())
    escolhidos = []
    for pos, qtd in FORMACAO.items():
        candidatos = sorted((a for a in atletas if a.posicao == pos), key=lambda a: (-(a.overall or 0), a.numero or 99, a.nome))
        escolhidos.extend(candidatos[:qtd])
    if len(escolhidos) < 11:                  # elenco desequilibrado: completa com os melhores restantes
        ids = {a.id for a in escolhidos}
        sobra = sorted((a for a in atletas if a.id not in ids and a.posicao != 'GOL'), key=lambda a: (-(a.overall or 0), a.nome))
        escolhidos.extend(sobra[:11 - len(escolhidos)])
    return escolhidos


def _validar_lado(atletas, time, rotulo):
    if len(atletas) != 11:
        raise ComparativoInvalido(f"Escolha exatamente 11 iniciais do {rotulo}.")
    if any(a.time_id != time.id for a in atletas):
        raise ComparativoInvalido(f"Há jogador que não é do {rotulo}.")
    contagem = Counter(a.posicao for a in atletas)
    if contagem['GOL'] != 1:
        raise ComparativoInvalido(f"O {rotulo} precisa de exatamente 1 goleiro entre os 11.")


@transaction.atomic
def criar(criador, time_a, time_b, ids_a, ids_b, titulo='', encerra_em=None):
    if time_a.pk == time_b.pk:
        raise ComparativoInvalido("Escolha dois times diferentes.")
    lado_a = list(Atleta.objects.filter(pk__in=ids_a))
    lado_b = list(Atleta.objects.filter(pk__in=ids_b))
    _validar_lado(lado_a, time_a, time_a.nome_exibicao)
    _validar_lado(lado_b, time_b, time_b.nome_exibicao)

    pool = Counter(a.posicao for a in lado_a + lado_b)
    for pos, minimo in FORMACAO.items():
        if pool[pos] < minimo:
            raise ComparativoInvalido(
                f"Com esses 22 não dá para montar um 4-3-3: faltam {minimo - pool[pos]} jogador(es) de {pos}.")

    comp = Comparativo.objects.create(criador=criador, time_a=time_a, time_b=time_b, titulo=titulo.strip()[:120], encerra_em=encerra_em)
    Escalacao.objects.bulk_create(
        [Escalacao(comparativo=comp, atleta=a, lado='A') for a in lado_a]
        + [Escalacao(comparativo=comp, atleta=a, lado='B') for a in lado_b])
    return comp


def candidatos(comp):
    """ Os 22 iniciais ordenados por lado e posição. """
    itens = list(comp.iniciais.select_related('atleta', 'atleta__time'))
    itens.sort(key=lambda e: (e.lado, ORDEM_POSICAO.get(e.atleta.posicao, 9), e.atleta.numero or 99, e.atleta.nome))
    return itens


@transaction.atomic
def votar(usuario, comp, atleta_ids):
    if not comp.aberto:
        raise ComparativoInvalido("Essa votação já encerrou.")
    ids = {int(i) for i in atleta_ids}
    pool = {e.atleta_id: e.atleta for e in candidatos(comp)}
    if not ids <= set(pool):
        raise ComparativoInvalido("Vote só nos jogadores da lista.")
    contagem = Counter(pool[i].posicao for i in ids)
    for pos, qtd in FORMACAO.items():
        if contagem[pos] != qtd:
            raise ComparativoInvalido(f"Escolha exatamente {qtd} de {pos} (você marcou {contagem[pos]}).")

    primeira = not Voto.objects.filter(comparativo=comp, usuario=usuario).exists()
    Voto.objects.filter(comparativo=comp, usuario=usuario).delete()
    Voto.objects.bulk_create([Voto(comparativo=comp, usuario=usuario, atleta_id=i) for i in ids])
    if primeira:
        coins.creditar(usuario, RECOMPENSA_VOTO, f"🗳️ Voto no 11 ideal: {comp}")
    return primeira


def meus_votos(usuario, comp):
    return set(Voto.objects.filter(comparativo=comp, usuario=usuario).values_list('atleta_id', flat=True))


def apuracao(comp):
    """
    Resultado parcial/final: o 11 eleito (mais votados por posição, empate = maior overall) e o placar
    de quantos eleitos vieram de cada time.
    """
    votos = Counter(Voto.objects.filter(comparativo=comp).values_list('atleta_id', flat=True))
    votantes = Voto.objects.filter(comparativo=comp).values('usuario').distinct().count()
    itens = candidatos(comp)
    por_pos = {}
    for e in itens:
        por_pos.setdefault(e.atleta.posicao, []).append(e)

    eleitos, linhas = [], []
    for pos in ('ATA', 'MEI', 'DEF', 'GOL'):                    # de cima para baixo no campo
        ordenados = sorted(por_pos.get(pos, []), key=lambda e: (-votos.get(e.atleta_id, 0), -(e.atleta.overall or 0), e.atleta.nome))
        escolhidos = ordenados[:FORMACAO[pos]]
        jogadores = [{'atleta': e.atleta, 'lado': e.lado, 'votos': votos.get(e.atleta_id, 0),
                      'pct': round(votos.get(e.atleta_id, 0) * 100 / votantes) if votantes else 0} for e in escolhidos]
        eleitos.extend(jogadores)
        linhas.append({'posicao': pos, 'jogadores': jogadores})

    placar = {'A': sum(1 for j in eleitos if j['lado'] == 'A'), 'B': sum(1 for j in eleitos if j['lado'] == 'B')}
    if not votantes:                           # sem votos não existe "eleito": nada de campeão por ordem de cadastro
        placar = {'A': 0, 'B': 0}
    ranking = sorted(({'atleta': e.atleta, 'lado': e.lado, 'votos': votos.get(e.atleta_id, 0)} for e in itens),
                     key=lambda x: -x['votos'])
    return {'votantes': votantes, 'linhas': linhas, 'placar': placar, 'ranking': ranking,
            'vencedor': 'A' if placar['A'] > placar['B'] else 'B' if placar['B'] > placar['A'] else None}

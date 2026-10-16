"""
Motor do "Vida de Craque": atributos, decisões, simulação das partidas e fechamento de temporada.
Puro e determinístico pela semente; a IA nunca decide números (ver servico.py).
"""
import math
import random

from .dados import CLUBES, EFEITOS, IDADE_INICIAL, MAX_TEMPORADAS, POSICOES, ROTULOS, TONS

ATRIBUTOS = ('tecnica', 'fisico', 'mental')
MEDIDORES = ('forma', 'moral', 'fama', 'torcida', 'tecnico')


def rng_de(semente, *partes):
    return random.Random(f'{semente}:' + ':'.join(map(str, partes)))


def poisson(rng, media):
    media = max(0.0, media)
    limite, k, p = math.exp(-media), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limite:
            return k
        k += 1


def clamp(x, a, b):
    return max(a, min(b, x))


def novo_estado(nome, posicao, clube, numero, semente):
    rng = rng_de(semente, 'inicio')
    base = rng.randint(54, 60)
    return {
        'nome': nome, 'posicao': posicao, 'numero': numero, 'clube': clube, 'idade': IDADE_INICIAL,
        'temporada': 1, 'rodada': 0, 'treinos': 0,
        'atrib': {'tecnica': base + rng.randint(-3, 4), 'fisico': base + rng.randint(-3, 4), 'mental': base + rng.randint(-4, 2)},
        'med': {'forma': 60, 'moral': 65, 'fama': 5, 'torcida': 40, 'tecnico': 50},
        'tempo': nova_temporada_stats(),
        'carreira': {'jogos': 0, 'gols': 0, 'assist': 0, 'titulos': [], 'premios': [], 'clubes': [clube]},
        'temporadas': [],
    }


def nova_temporada_stats():
    return {'jogos': 0, 'titular': 0, 'gols': 0, 'assist': 0, 'notas': [], 'v': 0, 'e': 0, 'd': 0}


def overall(estado):
    pt, pf, pm, _, _ = POSICOES[estado['posicao']]
    a = estado['atrib']
    return round(a['tecnica'] * pt + a['fisico'] * pf + a['mental'] * pm)


def aplicar(estado, efeitos, fator=1.0):
    """ Soma efeitos (limitados) e devolve só o que mudou, para mostrar ao jogador. """
    mudou = {}
    for chave, delta in efeitos.items():
        delta = round(delta * fator)
        if not delta:
            continue
        if chave in ATRIBUTOS:
            antes = estado['atrib'][chave]
            estado['atrib'][chave] = clamp(antes + delta, 30, 99)
            real = estado['atrib'][chave] - antes
        elif chave in MEDIDORES:
            antes = estado['med'][chave]
            estado['med'][chave] = clamp(antes + delta, 0, 100)
            real = estado['med'][chave] - antes
        else:
            continue
        if real:
            mudou[chave] = real
    return mudou


def efeito_da_decisao(efeito):
    return dict(EFEITOS.get(efeito, {}))


def efeito_do_tom(tom, qualidade):
    efeitos = dict(TONS.get(tom, {}))
    efeitos['fama'] = efeitos.get('fama', 0) + round((clamp(qualidade, 0, 10) - 5) / 2)
    return efeitos


def descrever(mudou):
    return [{'chave': k, 'rotulo': ROTULOS[k], 'delta': v} for k, v in mudou.items()]


def adversario(estado, rng):
    liga = CLUBES[estado['clube']][2]
    opcoes = [n for n, (_, _, l) in CLUBES.items() if l == liga and n != estado['clube']]
    return rng.choice(opcoes)


def simular_jogo(estado, semente):
    """ Simula a rodada atual e atualiza o estado. Devolve os fatos do jogo (o que a narração pode usar). """
    rng = rng_de(semente, 'jogo', estado['temporada'], estado['rodada'])
    med, ovr = estado['med'], overall(estado)
    forca = CLUBES[estado['clube']][0]
    rival = adversario(estado, rng)
    forca_rival = CLUBES[rival][0]
    em_casa = rng.random() < 0.5

    # escalação: nível do jogador contra o nível do elenco, relação com o técnico e forma
    chance = clamp(0.5 + (ovr - (forca - 12)) / 30 + (med['tecnico'] - 50) / 120 + (med['forma'] - 50) / 150, 0.08, 0.96)
    titular = rng.random() < chance
    minutos = 90 if titular else (rng.randint(12, 35) if rng.random() < 0.65 else 0)

    _, _, _, gols_90, assist_90 = POSICOES[estado['posicao']]
    impacto = (ovr / 70) ** 2 * (0.75 + med['forma'] / 200) * (forca / 80)
    gols = poisson(rng, gols_90 * impacto * minutos / 90) if minutos else 0
    assist = poisson(rng, assist_90 * impacto * minutos / 90) if minutos else 0

    mando = 0.25 if em_casa else -0.15
    gols_time = max(gols + assist, poisson(rng, max(0.3, 1.25 + (forca - forca_rival) / 25 + mando)) + gols)
    gols_rival = poisson(rng, max(0.25, 1.1 + (forca_rival - forca) / 25 - mando))
    resultado = 'V' if gols_time > gols_rival else 'E' if gols_time == gols_rival else 'D'

    nota = None
    if minutos:
        nota = 6.0 + gols * 1.1 + assist * 0.6 + (med['forma'] - 55) / 40 + rng.uniform(-0.8, 0.8)
        nota += {'V': 0.3, 'E': 0, 'D': -0.4}[resultado]
        nota = round(clamp(nota, 3.0, 10.0), 1)

    t = estado['tempo']
    t[resultado.lower()] += 1
    if minutos:
        t['jogos'] += 1
        t['titular'] += 1 if titular else 0
        t['gols'] += gols
        t['assist'] += assist
        t['notas'].append(nota)
        estado['carreira']['jogos'] += 1
        estado['carreira']['gols'] += gols
        estado['carreira']['assist'] += assist

    efeitos = {'forma': round(((nota or 5.5) - 6.2) * 4) if minutos else -2,
               'moral': {'V': 3, 'E': 0, 'D': -3}[resultado] + (2 if gols else 0) - (3 if not minutos else 0),
               'fama': gols * 2 + assist + (2 if nota and nota >= 8.5 else 0),
               'torcida': gols * 2 + {'V': 1, 'E': 0, 'D': -1}[resultado]}
    mudou = aplicar(estado, efeitos)
    fatos = {'rodada': estado['rodada'] + 1, 'temporada': estado['temporada'], 'clube': estado['clube'], 'rival': rival,
             'em_casa': em_casa, 'gols_time': gols_time, 'gols_rival': gols_rival, 'resultado': resultado,
             'titular': titular, 'minutos': minutos, 'gols': gols, 'assist': assist, 'nota': nota,
             'mudou': descrever(mudou)}
    estado['rodada'] += 1
    return fatos


def placar_texto(f):
    casa, fora = (f['clube'], f['rival']) if f['em_casa'] else (f['rival'], f['clube'])
    gc, gf = (f['gols_time'], f['gols_rival']) if f['em_casa'] else (f['gols_rival'], f['gols_time'])
    return f'{casa} {gc} x {gf} {fora}'


def narracao_pronta(estado, f):
    if not f['minutos']:
        papel = f"{estado['nome']} ficou no banco o jogo todo"
    elif not f['titular']:
        papel = f"{estado['nome']} entrou no segundo tempo ({f['minutos']} minutos)"
    else:
        papel = f"{estado['nome']} foi titular"
    lances = []
    if f['gols']:
        lances.append(f"marcou {f['gols']} gol{'s' if f['gols'] > 1 else ''}")
    if f['assist']:
        lances.append(f"deu {f['assist']} assistência{'s' if f['assist'] > 1 else ''}")
    detalhe = (' e ' + ' e '.join(lances)) if lances else ''
    fim = {'V': 'Vitória para levantar a torcida!', 'E': 'Empate com gosto de pouco.', 'D': 'Derrota dura de engolir.'}[f['resultado']]
    nota = f" Nota {str(f['nota']).replace('.', ',')}." if f['nota'] else ''
    return f"{placar_texto(f)}. {papel}{detalhe}.{nota} {fim}"


def manchete_pronta(estado, f):
    if f['gols'] >= 2:
        return f"{estado['nome']} decide e vira assunto na cidade"
    if f['gols']:
        return f"Gol de {estado['nome']} no {f['resultado'] == 'V' and 'triunfo' or 'jogo'} contra o {f['rival']}"
    if not f['minutos']:
        return f"Sem {estado['nome']} em campo, {estado['clube']} {({'V': 'vence', 'E': 'empata', 'D': 'perde'})[f['resultado']]}"
    return f"{estado['clube']} {({'V': 'vence', 'E': 'empata com', 'D': 'perde para'})[f['resultado']]} o {f['rival']}"


def fechar_temporada(estado, semente):
    """ Classificação, títulos, prêmios, evolução e propostas. Devolve o resumo da temporada. """
    t = estado['tempo']
    pontos = t['v'] * 3 + t['e']
    if pontos >= 24:
        colocacao = 'Campeão'
    elif pontos >= 19:
        colocacao = 'Vaga continental'
    elif pontos >= 12:
        colocacao = 'Meio da tabela'
    else:
        colocacao = 'Briga contra o rebaixamento'
    liga = CLUBES[estado['clube']][2]
    titulos, premios = [], []
    if colocacao == 'Campeão':
        titulos.append(f"{'Brasileirão' if liga == 'Brasileirão' else 'Liga europeia'} {estado['temporada']}")
    media = round(sum(t['notas']) / len(t['notas']), 2) if t['notas'] else 0
    if media >= 7.6 and t['jogos'] >= 6:
        premios.append('craque')
    if t['gols'] >= (7 if estado['posicao'] == 'Atacante' else 5):
        premios.append('artilheiro')
    if t['assist'] >= 5:
        premios.append('garcom')
    if estado['idade'] <= 19 and media >= 7.0 and t['jogos'] >= 5:
        premios.append('revelacao')
    estado['carreira']['titulos'] += titulos
    estado['carreira']['premios'] += premios

    resumo = {'temporada': estado['temporada'], 'clube': estado['clube'], 'idade': estado['idade'], 'pontos': pontos,
              'colocacao': colocacao, 'jogos': t['jogos'], 'titular': t['titular'], 'gols': t['gols'],
              'assist': t['assist'], 'media': media, 'titulos': titulos, 'premios': premios, 'overall': overall(estado)}
    estado['temporadas'].append(resumo)

    # evolução: jovem cresce, quem treinou cresce mais
    rng = rng_de(semente, 'evolucao', estado['temporada'])
    crescimento = 4 if estado['idade'] < 21 else 2 if estado['idade'] < 25 else 0
    bonus = min(3, estado['treinos'] // 3)
    for a in ('tecnica', 'fisico', 'mental'):
        estado['atrib'][a] = clamp(estado['atrib'][a] + crescimento + rng.randint(0, 1 + bonus), 30, 99)
    estado['idade'] += 1
    estado['treinos'] = 0
    estado['temporada'] += 1
    estado['rodada'] = 0
    estado['tempo'] = nova_temporada_stats()
    estado['med']['forma'] = 60
    estado['med']['moral'] = clamp(estado['med']['moral'] + (8 if titulos else 0), 0, 100)
    resumo['propostas'] = propostas(estado, rng)
    return resumo


def propostas(estado, rng):
    """ Clubes interessados: nível compatível com o jogador e com a fama dele. """
    alvo = overall(estado) + estado['med']['fama'] / 6
    candidatos = [n for n, (forca, _, _) in CLUBES.items()
                  if n != estado['clube'] and forca - 8 <= alvo + 4 and forca >= CLUBES[estado['clube']][0] - 2]
    rng.shuffle(candidatos)
    candidatos.sort(key=lambda n: -CLUBES[n][0])
    return candidatos[:3]


def transferir(estado, clube):
    estado['clube'] = clube
    if clube not in estado['carreira']['clubes']:
        estado['carreira']['clubes'].append(clube)
    estado['med']['tecnico'] = 50
    estado['med']['torcida'] = 35 + estado['med']['fama'] // 4


def carreira_acabou(estado):
    return estado['temporada'] > MAX_TEMPORADAS


def pontuacao(estado):
    c = estado['carreira']
    return c['gols'] * 3 + c['assist'] * 2 + len(c['titulos']) * 40 + len(c['premios']) * 25 + estado['med']['fama']


def premio_temporada(resumo):
    return min(50, 5 + len(resumo['titulos']) * 20 + len(resumo['premios']) * 10)

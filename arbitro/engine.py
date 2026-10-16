"""
Motor do Apito Final: monta a súmula de lances de uma partida e corrige as
decisões do jogador. Tudo aqui é puro (sem request) e determinístico pela semente.

Uma partida tem LANCES_POR_PARTIDA lances: alguns históricos (historicos.py) e o
resto gerado com geometria real, em que a resposta certa sai da regra:
impedimento, bola na linha, contato dentro/fora da área, falta e cartão e reinício.
"""
import copy
import random

from . import historicos
from .base import (ANIM_CAMPO_MS, ANIM_LINHA_MS, AREA_X, AREA_Y0, AREA_Y1, CATEGORIAS, COMPRIMENTO, LARGURA,
                   LIMITE_LINHA_CM, TRAVE_Y0, TRAVE_Y1, cena_campo, cena_linha, g_cartao, g_gol, g_impedimento,
                   g_marcacao, grupo, jogador as J, vista_de)

LANCES_POR_PARTIDA = 10
HISTORICOS_POR_PARTIDA = 4
GERADOS = ['impedimento', 'impedimento', 'linha', 'area', 'cartao', 'reinicio']

PONTOS_ACERTO = 100
PONTOS_PARCIAL = 40          # acertou parte (ex.: a marcação, mas errou o cartão)
FATOR_VAR = 0.6              # chamar o VAR ajuda, mas o lance vale menos
BONUS_TEMPO_MAX = 50
JANELA_TEMPO_MS = 20000      # decidiu na hora: bônus cai linearmente até zero em 20 s
BONUS_SEQUENCIA = 10         # por acerto seguido anterior
BONUS_SEQUENCIA_MAX = 50

TITULOS = [
    (10, 'Apito de Ouro', 'fa-crown'),
    (8, 'Árbitro FIFA', 'fa-earth-americas'),
    (6, 'Árbitro da Série A', 'fa-flag-checkered'),
    (4, 'Juiz de Várzea', 'fa-person-running'),
    (0, 'Vai pro VAR de vez', 'fa-tv'),
]


class RespostaInvalida(ValueError):
    pass


def _fmt_m(metros):
    cm = abs(metros) * 100
    return f'{cm:.0f} cm' if cm < 100 else f'{abs(metros):.1f} m'.replace('.', ',')


def _margem(rng, nivel, maior, menor):
    """ Margem da dúvida: começa folgada e aperta conforme a partida avança (nivel 0..1). """
    teto = maior - (maior - menor * 2.2) * nivel
    return rng.uniform(menor, max(menor * 1.2, teto))


# --------------------------------------------------------------------------------------- impedimento
def gerar_impedimento(rng, nivel):
    x_pen = rng.uniform(70, 90)                       # penúltimo defensor (goleiro é o último)
    m = _margem(rng, nivel, 2.2, 0.12) * rng.choice([-1, 1])
    variante = rng.choices(['passe', 'lateral', 'atras'], weights=[70, 15, 15])[0]
    if variante == 'atras':
        m = abs(m) + 0.2                              # à frente da defesa, mas atrás da bola
    x_at = x_pen + m
    y_at = rng.uniform(18, 50)

    ys_linha = sorted(rng.sample([12, 20, 28, 36, 44, 52, 58], 4))
    defensores = []
    recuos = [0] + [rng.uniform(0.3, 2.4) for _ in range(3)]
    rng.shuffle(recuos)
    for i, (y, rec) in enumerate(zip(ys_linha, recuos)):
        if abs(y - y_at) < 4:
            y += 6 if y < y_at else -6
        x = x_pen - rec
        defensores.append(J('d', [2, 3, 4, 6][i], (x, y), de=(x - 1.2, y), ate=(x + 2.5, y + rng.uniform(-1, 1))))
    goleiro = J('g', 1, (COMPRIMENTO - rng.uniform(2, 5), rng.uniform(31, 37)), de=(COMPRIMENTO - 3, 34),
                ate=(COMPRIMENTO - 5, 34))

    alvo = (min(COMPRIMENTO - 7, x_at + rng.uniform(6, 10)), y_at + rng.uniform(-3, 3))
    foco = J('a', 9, (x_at, y_at), de=(x_at - rng.uniform(1.5, 3), y_at + rng.uniform(-1, 1)), ate=alvo, foco=True)
    if variante == 'lateral':
        y_lat = rng.choice([0.3, LARGURA - 0.3])
        x_lat = x_pen - rng.uniform(4, 14)
        passador = J('a', 4, (x_lat, y_lat), de=(x_lat, y_lat), ate=(x_lat + 1, y_lat + (2 if y_lat < 1 else -2)))
        bola = ((x_lat, y_lat), (x_lat, y_lat), alvo)
        momento = 'COBRANÇA DO LATERAL'
        contexto = rng.choice([
            'Lateral rápido no campo de ataque: o lateral cobra com as mãos direto para o camisa 9, que já estava à frente da zaga.',
            'O time azul cobra o lateral longo para dentro da área; o camisa 9 domina nas costas dos zagueiros.',
        ])
    elif variante == 'atras':
        x_pas = min(COMPRIMENTO - 1.5, x_at + rng.uniform(2.5, 7))
        y_pas = rng.choice([rng.uniform(8, 14), rng.uniform(54, 60)])
        passador = J('a', 7, (x_pas, y_pas), de=(x_pas - 4, y_pas), ate=(x_pas + 0.5, y_pas))
        alvo = (x_at - rng.uniform(0.5, 2), y_at)
        foco['ate'] = [round(alvo[0], 2), round(alvo[1], 2)]
        bola = ((x_pas - 4, y_pas), (x_pas, y_pas), alvo)
        momento = 'MOMENTO DO PASSE'
        contexto = rng.choice([
            'O ponta chega à linha de fundo e rola para trás; o camisa 9 aparece batendo de primeira.',
            'Jogada pela ponta até o fundo e passe atrasado para o camisa 9, que vinha de trás da zaga.',
        ])
    else:
        x_pas = x_pen - rng.uniform(10, 20)
        y_pas = rng.uniform(20, 48)
        passador = J('a', 10, (x_pas, y_pas), de=(x_pas - 3, y_pas + rng.uniform(-2, 2)), ate=(x_pas + 1.5, y_pas))
        bola = ((x_pas - 3, y_pas), (x_pas + 0.6, y_pas), alvo)
        momento = 'MOMENTO DO PASSE'
        contexto = rng.choice([
            'Contra-ataque do time azul: o camisa 10 enfia a bola em profundidade para o camisa 9 (destacado).',
            'A zaga vermelha sobe para deixar o atacante impedido e o camisa 10 lança o camisa 9 (destacado).',
            'Bola enfiada entre os zagueiros; o camisa 9 (destacado) arranca na diagonal.',
        ])
    xo, yo = x_pen - rng.uniform(3, 8), rng.choice([10, 58])
    outro = J('a', 11, (xo, yo), de=(xo - 2.5, yo), ate=(xo + 4, yo + (4 if yo < 34 else -4)))
    xv, yv = passador['p'][0] + 3, min(LARGURA - 3, max(3, passador['p'][1] + rng.uniform(-6, 6)))
    volante = J('d', 5, (xv, yv), de=(xv + 2, yv), ate=(xv + 1, yv))
    jogadores = defensores + [goleiro, volante, outro, passador, foco]

    impedido = variante == 'passe' and m > 0
    if variante == 'lateral':
        motivo = 'Não existe impedimento em cobrança de lateral (nem em tiro de meta e escanteio).'
    elif variante == 'atras':
        motivo = (f'Ele estava {_fmt_m(m)} à frente do penúltimo defensor, mas atrás da linha da bola no momento do '
                  'passe: quem está atrás da bola nunca está impedido.')
    elif impedido:
        motivo = f'No momento do passe, o camisa 9 estava {_fmt_m(m)} à frente do penúltimo defensor: impedido.'
    else:
        motivo = f'No momento do passe, o camisa 9 estava {_fmt_m(m)} atrás do penúltimo defensor: posição legal.'
    pts_bola = [bola[0], bola[1], bola[2]]
    return {
        'chave': f'impedimento:{variante}', 'categoria': 'impedimento',
        'titulo': 'Impedimento?', 'contexto': contexto,
        'pergunta': 'O camisa 9 (destacado) estava em posição de impedimento?',
        'grupos': [g_impedimento()], 'correta': {'decisao': 'impedido' if impedido else 'legal'},
        'explicacao': motivo,
        'cena': cena_campo(vista_de(jogadores, pts_bola), jogadores, bola, momento),
        'var': {'linhas': [{'x': round(x_pen, 2), 't': 'd'}, {'x': round(x_at, 2), 't': 'a'}],
                'dica': 'Vale a posição no momento do passe. Compare com o penúltimo defensor (o goleiro conta) e '
                        'lembre: atrás da bola, ou em lateral, não há impedimento.'},
    }


# --------------------------------------------------------------------------------------- bola na linha
def gerar_linha(rng, nivel):
    eixo = rng.choices(['gol', 'fundo'], weights=[70, 30])[0]
    d = _margem(rng, nivel, 22, 0.8) * rng.choice([-1, 1])
    c = LIMITE_LINHA_CM + d
    passou = c > LIMITE_LINHA_CM
    if eixo == 'gol':
        contexto = rng.choice([
            'Chute forte de fora da área: a bola bate no travessão e quica perto da linha.',
            'Cabeçada no canto e o zagueiro tira de bicicleta em cima da linha.',
            'O goleiro espalma e a bola fica quicando na linha antes de ser afastada.',
        ])
        grupos, correta = [g_gol()], {'decisao': 'gol' if passou else 'nao_gol'}
        pergunta = 'A bola entrou inteira? Foi gol?'
        fim = 'Gol.' if passou else 'Não foi gol.'
    else:
        contexto = rng.choice([
            'O ponta corre atrás da bola até a linha de fundo e cruza de primeira; o centroavante marca.',
            'Bola esticada para o fundo; o lateral se joga, alcança e cruza para o gol.',
        ])
        grupos = [grupo('decisao', 'Decisão', ('saiu', 'Saiu: anular o gol'), ('em_jogo', 'Em jogo: gol válido'))]
        correta = {'decisao': 'saiu' if passou else 'em_jogo'}
        pergunta = 'A bola saiu antes do cruzamento?'
        fim = 'Ela saiu: o gol não vale.' if passou else 'Ela ainda estava em jogo: o gol vale.'
    borda = c - 11 - 12
    if passou:
        detalhe = f'A borda da bola mais perto do campo ficou {abs(borda):.0f} cm além da linha.'
    else:
        detalhe = f'Faltaram {abs(borda):.0f} cm para a bola inteira passar da linha inteira.'
    return {
        'chave': f'linha:{eixo}', 'categoria': 'linha',
        'titulo': 'Gol ou não?' if eixo == 'gol' else 'Saiu ou não?', 'contexto': contexto, 'pergunta': pergunta,
        'grupos': grupos, 'correta': correta,
        'explicacao': f'{detalhe} {fim} A linha faz parte do campo: só conta quando a bola inteira passa da linha inteira.',
        'cena': cena_linha(c, eixo, rng.uniform(-40, 40), rng.choice(['quique', 'rasteira'])),
        'var': {'zoom': True, 'dica': 'A bola inteira precisa ultrapassar a linha inteira. Compare a borda da bola mais '
                                      'próxima do campo com a borda de fora da linha.'},
    }


# --------------------------------------------------------------------------------------- dentro ou fora da área
def gerar_area(rng, nivel):
    d = _margem(rng, nivel, 2.4, 0.06) * rng.choice([-1, 1])       # > 0: dentro da área (a linha é da área)
    if rng.random() < 0.7:
        cx, cy = AREA_X + d, rng.uniform(AREA_Y0 + 4, AREA_Y1 - 4)
        dir_x, dir_y = 1, 0
    else:
        lado_baixo = rng.random() < 0.5
        cy = (AREA_Y1 - d) if lado_baixo else (AREA_Y0 + d)
        cx = rng.uniform(AREA_X + 3, COMPRIMENTO - 4)
        dir_x, dir_y = 0, (-1 if lado_baixo else 1)
    dentro = d > 0
    # cai sempre para dentro: o "pulo" para a área engana quem olha onde o jogador terminou
    queda = (cx + dir_x * rng.uniform(1.2, 2.2) + dir_y * 0.3, cy + dir_y * rng.uniform(1.2, 2.2))
    origem = (cx - dir_x * 8 - dir_y * 2, cy - dir_y * 8 + rng.uniform(-2, 2) * dir_x)
    atacante = J('a', 7, (cx, cy), de=origem, ate=queda, foco=True, cai=True)
    marc = (cx - dir_x * 0.6 + dir_y * 0.5, cy - dir_y * 0.6 + 0.5 * dir_x)
    defensor = J('d', 3, marc, de=(marc[0] - dir_x * 3 + 2 * dir_y, marc[1] - dir_y * 3 + 2.5 * dir_x),
                 ate=(marc[0] + dir_x * 0.8, marc[1] + dir_y * 0.8))
    jogadores = [
        defensor, atacante,
        J('g', 1, (COMPRIMENTO - 2, 34), de=(COMPRIMENTO - 1.5, 34), ate=(COMPRIMENTO - 2.5, 34)),
        J('d', 4, (AREA_X + 6, 30), de=(AREA_X + 6, 31), ate=(AREA_X + 7, 31)),
        J('a', 9, (AREA_X + 3, 38), de=(AREA_X - 1, 38), ate=(AREA_X + 6, 37)),
    ]
    bola = (origem, (cx + dir_x * 0.6, cy + dir_y * 0.6), (cx + dir_x * 3, cy + dir_y * 3 + 0.5))
    distancia = _fmt_m(d)
    if dentro:
        motivo = f'O contato foi {distancia} para dentro da borda da área (a linha faz parte da área): pênalti.'
    else:
        motivo = f'O contato foi {distancia} antes da linha da área: tiro livre, mesmo com o atacante caindo lá dentro.'
    return {
        'chave': 'area', 'categoria': 'area',
        'titulo': 'Dentro ou fora?',
        'contexto': rng.choice([
            'O ponta azul parte em velocidade e o zagueiro dá o carrinho pegando o pé dele, sem tocar a bola. '
            'Falta clara. Mas onde?',
            'Drible curto na entrada da área e o marcador derruba o atacante com um calço. Ninguém duvida da falta.',
        ]),
        'pergunta': 'É pênalti ou tiro livre fora da área?',
        'grupos': [grupo('marcacao', 'Marcação', ('falta', 'Tiro livre fora da área'), ('penalti', 'Pênalti'))],
        'correta': {'marcacao': 'penalti' if dentro else 'falta'},
        'explicacao': motivo + ' Vale o lugar do contato, não onde o jogador cai.',
        'cena': cena_campo([AREA_X - 14, AREA_Y0 - 9, COMPRIMENTO + 3, AREA_Y1 + 9], jogadores, bola, 'CONTATO',
                           contato=(cx, cy)),
        'var': {'zoom': {'x': round(cx, 2), 'y': round(cy, 2), 'r': 3},
                'dica': 'Vale onde aconteceu o contato, não onde o jogador caiu. A linha faz parte da área.'},
    }


# --------------------------------------------------------------------------------------- falta e cartão (regra 12)
INFRACOES = {
    'disputa': ('tenta tirar a bola de carrinho, sem violência, mas chega um pouco atrasado e derruba o atacante', True),
    'puxao': ('agarra a camisa do atacante e o puxa até derrubá-lo, sem nenhuma chance de jogar a bola', False),
    'violenta': ('entra de sola, com as travas na altura do tornozelo e com força excessiva', True),
}
OPORTUNIDADES = {
    'clara': 'Ele estava sozinho, cara a cara com o goleiro, com o gol à sua frente.',
    'promissora': 'Era um ataque promissor, mas ainda havia dois defensores na cobertura.',
    'comum': 'Era uma jogada sem perigo, longe do gol, com a defesa toda postada.',
}


def decidir_cartao(infracao, oportunidade, dentro):
    """ Regra 12: jogada brusca grave, DOGSO (oportunidade clara) e SPA (ataque promissor), com a redução na área. """
    if infracao == 'violenta':
        return 'vermelho', 'Jogada brusca grave (força excessiva) é vermelho direto, em qualquer lugar.'
    tentou_bola = INFRACOES[infracao][1]
    if oportunidade == 'clara':
        if not dentro:
            return 'vermelho', 'Impedir uma oportunidade clara de gol fora da área é vermelho.'
        if tentou_bola:
            return 'amarelo', ('Dentro da área, se o defensor tentou jogar a bola, o pênalti já compensa: a oportunidade '
                               'clara de gol vira amarelo.')
        return 'vermelho', 'Dentro da área, sem tentar jogar a bola (puxão), impedir oportunidade clara continua vermelho.'
    if oportunidade == 'promissora':
        if not dentro:
            return 'amarelo', 'Parar um ataque promissor com falta é amarelo.'
        if tentou_bola:
            return 'nenhum', 'Dentro da área, tentando jogar a bola, o pênalti basta: o amarelo do ataque promissor cai.'
        return 'amarelo', 'Dentro da área, sem tentar jogar a bola, o ataque promissor interrompido ainda é amarelo.'
    return 'nenhum', 'Falta comum, por descuido, sem ataque promissor: sem cartão.'


def gerar_cartao(rng, nivel):
    oportunidade = rng.choices(['clara', 'promissora', 'comum'], weights=[45, 40, 15])[0]
    infracao = rng.choices(['disputa', 'puxao', 'violenta'], weights=[45, 40, 15])[0]
    if oportunidade == 'comum':
        infracao = rng.choice(['disputa', 'violenta'])
        dentro = False
        cx, cy = rng.uniform(45, 62), rng.uniform(14, 54)
    else:
        dentro = rng.random() < 0.5
        cx = rng.uniform(AREA_X + 3, COMPRIMENTO - 7) if dentro else rng.uniform(AREA_X - 18, AREA_X - 4)
        cy = rng.uniform(AREA_Y0 + 8, AREA_Y1 - 8)
    cartao, motivo = decidir_cartao(infracao, oportunidade, dentro)
    texto_infr, _ = INFRACOES[infracao]

    atacante = J('a', 11, (cx, cy), de=(cx - 9, cy + rng.uniform(-3, 3)), ate=(cx + 1.6, cy + 0.6), foco=True, cai=True)
    infrator = J('d', 4, (cx - 0.7, cy + 0.6), de=(cx - 6, cy + 4), ate=(cx + 0.4, cy + 0.9))
    jogadores = [atacante, infrator, J('g', 1, (COMPRIMENTO - 3, 34), de=(COMPRIMENTO - 2, 34), ate=(COMPRIMENTO - 4, 34))]
    if oportunidade == 'promissora':
        xc = cx + (COMPRIMENTO - 3 - cx) * 0.55          # cobertura entre o lance e o gol
        jogadores += [J('d', 3, (xc, cy - 6), de=(xc - 2, cy - 6), ate=(xc - 1, cy - 5)),
                      J('d', 5, (xc - 1, cy + 7), de=(xc - 3, cy + 7), ate=(xc - 2, cy + 5))]
    elif oportunidade == 'comum':
        jogadores += [J('d', n, (cx + dx, cy + dy), de=(cx + dx - 1, cy + dy), ate=(cx + dx, cy + dy))
                      for n, dx, dy in ((2, 10, -12), (3, 12, -3), (5, 11, 6), (6, 9, 14), (8, 5, -6))]
    bola = ((cx - 8.6, cy), (cx + 0.5, cy), (cx + 3.5, cy - 0.5))
    onde = 'dentro da área' if dentro else ('fora da área' if oportunidade != 'comum' else 'no meio-campo')
    marcacao = 'penalti' if dentro else 'falta'
    return {
        'chave': f'cartao:{oportunidade}:{infracao}', 'categoria': 'cartao',
        'titulo': 'Falta e cartão',
        'contexto': f'{OPORTUNIDADES[oportunidade]} O zagueiro {texto_infr}, {onde}.',
        'pergunta': 'Qual a marcação e o cartão?',
        'grupos': [g_marcacao(), g_cartao()], 'correta': {'marcacao': marcacao, 'cartao': cartao},
        'explicacao': f'{"Pênalti" if dentro else "Tiro livre"}. {motivo}',
        'cena': cena_campo(vista_de(jogadores, list(bola), minimo=40), jogadores, bola, 'CONTATO', contato=(cx - 0.2, cy + 0.3)),
        'var': {'zoom': {'x': round(cx, 2), 'y': round(cy, 2), 'r': 5},
                'dica': 'Pergunte: era oportunidade clara de gol ou ataque promissor? Dentro da área, o defensor tentou '
                        'jogar a bola? Força excessiva é sempre vermelho.'},
    }


# --------------------------------------------------------------------------------------- reinício
def gerar_reinicio(rng, nivel):
    tipo = rng.choices(['fundo', 'lateral'], weights=[65, 35])[0]
    ultimo = rng.choice(['a', 'd', 'g'] if tipo == 'fundo' else ['a', 'd'])
    grupos = [grupo('decisao', 'Reinício', ('escanteio', 'Escanteio'), ('tiro_meta', 'Tiro de meta'),
                    ('lateral_azul', 'Lateral para o azul'), ('lateral_vermelho', 'Lateral para o vermelho'))]
    if tipo == 'fundo':
        y_saida = rng.choice([rng.uniform(18, TRAVE_Y0 - 2), rng.uniform(TRAVE_Y1 + 2, 50)])
        chute = (rng.uniform(80, 88), rng.uniform(22, 46))
        if ultimo == 'g':
            toque = (COMPRIMENTO - 1.5, (TRAVE_Y0 + TRAVE_Y1) / 2 + (2.5 if y_saida > 34 else -2.5))
        else:
            toque = (rng.uniform(95, 100), (chute[1] + y_saida) / 2 + rng.uniform(-2, 2))
        jogadores = [
            J('a', 9, chute, de=(chute[0] - 4, chute[1]), ate=(chute[0] + 3, chute[1]), toque=ultimo == 'a', foco=ultimo == 'a'),
            J('d', 3, toque if ultimo == 'd' else (toque[0] - 2, toque[1] - 5),
              de=(toque[0] - 3, toque[1]), ate=(toque[0] + 1, toque[1]), toque=ultimo == 'd', foco=ultimo == 'd'),
            J('g', 1, toque if ultimo == 'g' else (COMPRIMENTO - 2, 34), de=(COMPRIMENTO - 2, 34),
              ate=(toque[0] if ultimo == 'g' else COMPRIMENTO - 2, toque[1] if ultimo == 'g' else 34),
              toque=ultimo == 'g', foco=ultimo == 'g'),
            J('d', 5, (AREA_X + 2, 40), de=(AREA_X, 40), ate=(AREA_X + 4, 39)),
        ]
        if ultimo == 'a':
            bola = ((chute[0] - 4, chute[1]), chute, (COMPRIMENTO + 2.5, y_saida))
        else:
            bola = ((chute[0] - 4, chute[1]), toque, (COMPRIMENTO + 2.5, y_saida + (toque[1] - chute[1]) * 0.3))
        correta = 'tiro_meta' if ultimo == 'a' else 'escanteio'
        contexto = rng.choice([
            'O camisa 9 azul chuta cruzado da entrada da área e a bola sai pela linha de fundo.',
            'Finalização do time azul que passa raspando por quem estava no caminho e sai pela linha de fundo.',
        ])
        quem = {'a': 'do atacante azul', 'd': 'do zagueiro vermelho', 'g': 'do goleiro vermelho'}[ultimo]
        explicacao = (f'O último toque foi {quem}. '
                      + ('Bola que sai pela linha de fundo tocada por último pelo ataque é tiro de meta.' if ultimo == 'a'
                         else 'Bola que sai pela linha de fundo tocada por último pela defesa (goleiro incluso) é escanteio.'))
        momento = 'ÚLTIMO TOQUE'
        vista = [AREA_X - 14, 8, COMPRIMENTO + 3, 60]
    else:
        x = rng.uniform(30, 75)
        y_lado = LARGURA if rng.random() < 0.5 else 0
        sinal = 1 if y_lado == LARGURA else -1
        disputa = (x, y_lado - sinal * rng.uniform(3, 6))
        a = J('a', 7, disputa if ultimo == 'a' else (disputa[0] - 1, disputa[1] + sinal * 0.2),
              de=(x - 6, disputa[1] - sinal * 4), ate=(x + 1, disputa[1]), toque=ultimo == 'a', foco=ultimo == 'a')
        d = J('d', 2, disputa if ultimo == 'd' else (disputa[0] + 1, disputa[1] + sinal * 0.2),
              de=(x + 5, disputa[1] - sinal * 3), ate=(x + 0.5, disputa[1] + sinal * 1), toque=ultimo == 'd', foco=ultimo == 'd')
        jogadores = [a, d, J('a', 10, (x - 10, 34), de=(x - 12, 34), ate=(x - 9, 34)),
                     J('d', 6, (x + 8, 34 + sinal * 6), de=(x + 9, 34), ate=(x + 7, 34 + sinal * 6))]
        bola = ((x - 6, disputa[1] - sinal * 4), disputa, (x + 2, y_lado + sinal * 2.5))
        correta = 'lateral_vermelho' if ultimo == 'a' else 'lateral_azul'
        contexto = 'Dividida perto da lateral entre o camisa 7 azul e o camisa 2 vermelho; a bola sai pela linha lateral.'
        explicacao = (f'Quem tocou por último foi o {"camisa 7 azul" if ultimo == "a" else "camisa 2 vermelho"}: '
                      f'o lateral é do adversário, o {"vermelho" if ultimo == "a" else "azul"}.')
        momento = 'ÚLTIMO TOQUE'
        vista = [max(0, x - 22), 0, min(COMPRIMENTO, x + 22), LARGURA]
    return {
        'chave': f'reinicio:{tipo}:{ultimo}', 'categoria': 'reinicio',
        'titulo': 'Como o jogo recomeça?', 'contexto': contexto,
        'pergunta': 'Qual é o reinício correto?',
        'grupos': grupos, 'correta': {'decisao': correta}, 'explicacao': explicacao,
        'cena': cena_campo(vista, jogadores, bola, momento),
        'var': {'dica': 'Reveja quem tocou por último (fica destacado no replay). Goleiro conta como defesa.'},
    }


GERADORES = {
    'impedimento': gerar_impedimento, 'linha': gerar_linha, 'area': gerar_area,
    'cartao': gerar_cartao, 'reinicio': gerar_reinicio,
}


# --------------------------------------------------------------------------------------- partida
def _anim(lance):
    return ANIM_LINHA_MS if lance['cena']['tipo'] == 'linha' else ANIM_CAMPO_MS


def gerar_partida(semente, evitar=()):
    """ Lista de lances (completos, com gabarito). `evitar`: chaves históricas vistas por último. """
    rng = random.Random(semente)
    hist = historicos.todos()
    novos = [h for h in hist if h['chave'] not in set(evitar)]
    pool = novos if len(novos) >= HISTORICOS_POR_PARTIDA else hist
    escolhidos = rng.sample(pool, HISTORICOS_POR_PARTIDA)
    gerados = list(GERADOS)
    rng.shuffle(gerados)
    # históricos espalhados pela partida (posições 1, 4, 6 e 9, por exemplo), nunca dois seguidos no começo
    slots = sorted(rng.sample(range(LANCES_POR_PARTIDA), HISTORICOS_POR_PARTIDA))
    lances = []
    for i in range(LANCES_POR_PARTIDA):
        nivel = i / (LANCES_POR_PARTIDA - 1)
        if i in slots:
            lance = copy.deepcopy(escolhidos[slots.index(i)])
        else:
            lance = GERADORES[gerados.pop()](rng, nivel)
            lance['historico'] = False
        lance['anim_ms'] = _anim(lance)
        lances.append(lance)
    return lances


def publico(lance, indice, total):
    """ O que o navegador pode ver antes da resposta: sem gabarito, sem explicação, sem VAR. """
    rotulo, icone = CATEGORIAS[lance['categoria']]
    return {
        'indice': indice, 'total': total, 'categoria': rotulo, 'icone': icone, 'historico': lance['historico'],
        'titulo': lance['titulo'], 'contexto': lance['contexto'], 'pergunta': lance['pergunta'],
        'grupos': lance['grupos'], 'cena': lance['cena'], 'anim_ms': lance['anim_ms'],
        'tem_var': bool(lance.get('var')),
    }


def var_publico(lance):
    v = lance.get('var') or {}
    return {k: v[k] for k in ('linhas', 'zoom', 'dica') if k in v}


def rotulos_corretos(lance):
    saida = []
    for g in lance['grupos']:
        opcoes = dict(map(tuple, g['opcoes']))
        saida.append({'grupo': g['rotulo'], 'resposta': opcoes[lance['correta'][g['id']]]})
    return saida


def validar_resposta(lance, resposta):
    if not isinstance(resposta, dict):
        raise RespostaInvalida('Resposta em formato inválido.')
    limpa = {}
    for g in lance['grupos']:
        escolha = resposta.get(g['id'])
        if escolha not in {o[0] for o in g['opcoes']}:
            raise RespostaInvalida(f'Escolha uma opção em “{g["rotulo"]}”.')
        limpa[g['id']] = escolha
    return limpa


def avaliar(lance, resposta, tempo_ms, var_usado, sequencia):
    """ Corrige a decisão. `sequencia` = acertos seguidos antes deste lance. """
    resposta = validar_resposta(lance, resposta)
    certos = sum(1 for gid, op in resposta.items() if lance['correta'][gid] == op)
    acertou = certos == len(lance['grupos'])
    parcial = not acertou and certos > 0
    fator = FATOR_VAR if var_usado else 1
    base = bonus_tempo = bonus_seq = 0
    if acertou:
        base = round(PONTOS_ACERTO * fator)
        tempo_ms = max(0, int(tempo_ms))
        bonus_tempo = round(BONUS_TEMPO_MAX * max(0.0, 1 - tempo_ms / JANELA_TEMPO_MS) * fator)
        bonus_seq = min(BONUS_SEQUENCIA_MAX, BONUS_SEQUENCIA * sequencia)
    elif parcial:
        base = round(PONTOS_PARCIAL * fator)
    return {
        'resposta': resposta, 'acertou': acertou, 'parcial': parcial,
        'pontos': base + bonus_tempo + bonus_seq, 'base': base, 'bonus_tempo': bonus_tempo, 'bonus_seq': bonus_seq,
    }


def titulo_arbitro(acertos):
    for minimo, nome, icone in TITULOS:
        if acertos >= minimo:
            return {'nome': nome, 'icone': icone}
    return {'nome': TITULOS[-1][1], 'icone': TITULOS[-1][2]}


def premio(acertos):
    """ Cartola Coins ao fim da partida. """
    return acertos * 3 + (30 if acertos == LANCES_POR_PARTIDA else 0)

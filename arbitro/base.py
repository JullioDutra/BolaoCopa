"""
Peças comuns dos lances do Apito Final: medidas do campo, grupos de resposta e
construtores das cenas 2D.

Coordenadas do campo em metros, vista de cima: x de 0 a 105 (o time azul ataca
para a direita, gol em x = 105) e y de 0 a 68. A cena "linha" (câmera da linha
do gol) usa centímetros: `c` é a distância do centro da bola até a borda da
linha do lado do campo (positivo = para dentro do gol / para fora do campo).
"""

COMPRIMENTO, LARGURA = 105.0, 68.0
AREA_X = COMPRIMENTO - 16.5                # borda externa da linha da grande área
AREA_Y0, AREA_Y1 = 13.84, 54.16
TRAVE_Y0, TRAVE_Y1 = 30.34, 37.66
LINHA_CM, BOLA_RAIO_CM = 12, 11
LIMITE_LINHA_CM = LINHA_CM + BOLA_RAIO_CM  # centro da bola além disso = bola inteira passou da linha inteira

ANIM_CAMPO_MS, ANIM_LINHA_MS = 4200, 2200

CATEGORIAS = {
    'impedimento': ('Impedimento', 'fa-flag'),
    'linha': ('Gol ou não?', 'fa-bullseye'),
    'area': ('Dentro ou fora?', 'fa-vector-square'),
    'cartao': ('Falta e cartão', 'fa-square'),
    'reinicio': ('Reinício de jogo', 'fa-rotate'),
    'mao': ('Mão na bola', 'fa-hand'),
    'conduta': ('Disciplina', 'fa-gavel'),
}


def grupo(gid, rotulo, *opcoes):
    return {'id': gid, 'rotulo': rotulo, 'opcoes': [list(o) for o in opcoes]}


def g_marcacao():
    return grupo('marcacao', 'Marcação', ('nada', 'Segue o jogo'), ('falta', 'Tiro livre'), ('penalti', 'Pênalti'))


def g_cartao():
    return grupo('cartao', 'Cartão', ('nenhum', 'Sem cartão'), ('amarelo', 'Amarelo'), ('vermelho', 'Vermelho'))


def g_gol():
    return grupo('decisao', 'Decisão', ('gol', 'Gol!'), ('nao_gol', 'Não foi gol'))


def g_validar():
    return grupo('decisao', 'Decisão', ('gol', 'Gol válido'), ('anular', 'Anular o gol'))


def g_impedimento():
    return grupo('decisao', 'Decisão', ('impedido', 'Impedido'), ('legal', 'Posição legal'))


def r(x, nd=2):
    return round(float(x), nd)


def jogador(t, n, p, de=None, ate=None, nome='', foco=False, cai=False, toque=False):
    """ t: 'a' (ataque, azul), 'd' (defesa, vermelho) ou 'g' (goleiro da defesa). """
    j = {'t': t, 'n': str(n), 'p': [r(p[0]), r(p[1])]}
    if de:
        j['de'] = [r(de[0]), r(de[1])]
    if ate:
        j['ate'] = [r(ate[0]), r(ate[1])]
    for chave, valor in (('nome', nome), ('foco', foco), ('cai', cai), ('toque', toque)):
        if valor:
            j[chave] = valor
    return j


def cena_campo(vista, jogadores, bola, momento, contato=None, mao=None, cores=None):
    """ bola = (de, p, ate): `p` é a posição no instante congelado; `ate` pode ser uma lista de pontos. """
    de, p, ate = bola
    if ate and isinstance(ate[0], (list, tuple)):
        ate = [[r(a[0]), r(a[1])] for a in ate]
    elif ate:
        ate = [[r(ate[0]), r(ate[1])]]
    c = {'tipo': 'campo', 'vista': [r(v, 1) for v in vista], 'jogadores': jogadores,
         'bola': {'de': [r(de[0]), r(de[1])], 'p': [r(p[0]), r(p[1])], 'ate': ate or []}, 'momento': momento}
    if contato:
        c['contato'] = [r(contato[0]), r(contato[1])]
    if mao:
        c['mao'] = [r(mao[0]), r(mao[1])]
    if cores:
        c['cores'] = cores
    return c


def cena_linha(c, eixo='gol', y=0, origem='quique'):
    return {'tipo': 'linha', 'eixo': eixo, 'c': r(c, 1), 'y': r(y, 1), 'origem': origem}


def vista_de(jogadores, bola_pts, margem=6, minimo=34):
    """ Recorte justo do campo com todos os jogadores e a bola (o gol entra quando a jogada está perto dele). """
    pts = [p for j in jogadores for p in (j['p'], j.get('de', j['p']), j.get('ate', j['p']))] + [list(b) for b in bola_pts]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1 = min(xs) - margem, max(xs) + margem
    y0, y1 = min(ys) - margem, max(ys) + margem
    if x1 > COMPRIMENTO - 12:
        x1 = COMPRIMENTO + 3
    if x1 - x0 < minimo:
        meio = (x0 + x1) / 2
        x0, x1 = meio - minimo / 2, meio + minimo / 2
    if y1 - y0 < minimo * 0.62:
        meio = (y0 + y1) / 2
        y0, y1 = meio - minimo * 0.31, meio + minimo * 0.31
    return [max(-3.0, x0), max(-3.0, y0), min(COMPRIMENTO + 3, x1), min(LARGURA + 3, y1)]

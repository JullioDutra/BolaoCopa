"""
Motor de simulação do "7 a 0".

Funções puras sobre um `estado` (dict serializável em JSON). Cada minuto usa um sorteio determinístico
derivado de (seed, período, minuto): reabrir ou reprocessar a mesma partida dá o mesmo jogo, e os testes
conseguem reproduzir resultados.

Ideia geral de cada minuto:
  1. Quem tem mais "meio" tem mais posse e, portanto, mais chances de montar um ataque.
  2. O ataque vira finalização conforme ataque x defesa (ratio).
  3. A finalização vai no alvo conforme o finalizador; o gol sai conforme finalizador x goleiro.
  4. Faltas, cartões, pênaltis, lesões e cansaço mexem na força de cada lado.
"""
import random

from . import dados, narracao

LADOS = ('casa', 'fora')
MENTALIDADES = {
    #                ataque  exposição(do rival atacar)  faltas
    'retranca':    {'ataque': 0.72, 'expo': 0.78, 'faltas': 0.9, 'nome': 'Retranca'},
    'equilibrado': {'ataque': 1.00, 'expo': 1.00, 'faltas': 1.0, 'nome': 'Equilibrado'},
    'ofensivo':    {'ataque': 1.22, 'expo': 1.14, 'faltas': 1.1, 'nome': 'Ofensivo'},
    'tudo':        {'ataque': 1.55, 'expo': 1.40, 'faltas': 1.25, 'nome': 'Tudo ou nada'},
}
ESTILOS = {
    #            posse  conversão  fadiga  faltas
    'posse':    {'posse': 1.10, 'conv': 1.00, 'fadiga': 0.9, 'faltas': 0.9, 'nome': 'Toque de bola'},
    'contra':   {'posse': 0.92, 'conv': 1.10, 'fadiga': 1.0, 'faltas': 1.0, 'nome': 'Contra-ataque'},
    'pressao':  {'posse': 1.04, 'conv': 1.00, 'fadiga': 1.35, 'faltas': 1.3, 'nome': 'Pressão alta'},
}
PESO_FINALIZADOR = {'ATA': 3.0, 'PON': 2.2, 'MEI': 1.4, 'VOL': 0.55, 'LAT': 0.45, 'ZAG': 0.35, 'GOL': 0.0}
PESO_FALTA = {'ZAG': 1.0, 'VOL': 1.3, 'LAT': 1.0, 'MEI': 0.8, 'PON': 0.5, 'ATA': 0.4, 'GOL': 0.1}

BASE_ATAQUE = 0.165      # probabilidade-base (por minuto, por lado) de montar um ataque
LIMITE_SUBS = 5
MAX_ACRESCIMO = {1: 3, 2: 6}


# ------------------------------------------------------------------ estado

def novo_estado(casa, fora, seed, usuario_lado=None, mata_mata=False):
    """ casa/fora: dict {'time': chave, 'formacao', 'mentalidade', 'estilo', 'titulares': [nomes] ou None}. """
    rng = random.Random(f'acrescimos-{seed}')
    estado = {
        'seed': seed, 'periodo': 1, 'minuto': 0, 'status': 'pre', 'usuario_lado': usuario_lado, 'mata_mata': mata_mata,
        'acrescimo': {'1': rng.randint(1, MAX_ACRESCIMO[1]), '2': rng.randint(2, MAX_ACRESCIMO[2])},
        'placar': {'casa': 0, 'fora': 0}, 'eventos': [], 'lados': {}, 'notas': {},
        'stats': {l: {'chutes': 0, 'no_alvo': 0, 'posse': 0.0, 'faltas': 0, 'escanteios': 0,
                      'amarelos': 0, 'vermelhos': 0, 'defesas': 0} for l in LADOS},
    }
    for lado, cfg in (('casa', casa), ('fora', fora)):
        time = cfg.get('time_obj') or dados.obter(cfg['time'])
        formacao = cfg.get('formacao') or time['formacao']
        xi = dados.escalar(time, formacao, cfg.get('titulares'))
        nomes = [j['nome'] for j in xi]
        estado['lados'][lado] = {
            'time': cfg['time'], 'formacao': formacao,
            'mentalidade': cfg.get('mentalidade') or 'equilibrado', 'estilo': cfg.get('estilo') or 'posse',
            'nome_time': time['nome'], 'cor': time['cor'], 'clube': time['clube'], 'ano': time['ano'], 'elenco': time['elenco'],
            'titulares': nomes, 'banco': [j['nome'] for j in time['elenco'] if j['nome'] not in nomes],
            'expulsos': [], 'lesionados': [], 'subs': 0, 'amarelos': {}, 'saiu': [],
        }
        for n in nomes:
            estado['notas'][n] = 6.0
    return estado


def _jogador(lado_estado, nome):
    elenco = lado_estado.get('elenco') or dados.obter(lado_estado['time'])['elenco']
    return next(j for j in elenco if j['nome'] == nome)


def em_campo(estado, lado):
    l = estado['lados'][lado]
    fora = set(l['expulsos']) | set(l['lesionados'])
    return [_jogador(l, n) for n in l['titulares'] if n not in fora]


def minuto_texto(estado):
    p, m = estado['periodo'], estado['minuto']
    limite = 45 if p == 1 else 90
    return f"{limite}+{m - limite}" if m > limite else str(m)


# ------------------------------------------------------------------ forças

def _fadiga(estado, lado):
    l = estado['lados'][lado]
    m = max(0, estado['minuto'] - 55)
    fad = m * 0.0022 * ESTILOS[l['estilo']]['fadiga'] - 0.012 * l['subs']
    return max(0.0, min(0.12, fad))


def forca_lado(estado, lado):
    xi = em_campo(estado, lado)
    f = dados.forcas(xi)
    n = len(xi)
    homens = (n / 11) ** 0.7 if n < 11 else 1.0
    fad = 1 - _fadiga(estado, lado)
    return {k: (v if k == 'gol' else v * homens * fad) for k, v in f.items()}, xi


def _escolhe(rng, jogadores, pesos):
    total = sum(pesos)
    if total <= 0:
        return rng.choice(jogadores)
    x = rng.random() * total
    acc = 0
    for j, p in zip(jogadores, pesos):
        acc += p
        if x <= acc:
            return j
    return jogadores[-1]


def _nota(estado, nome, delta):
    estado['notas'][nome] = round(min(10.0, max(3.0, estado['notas'].get(nome, 6.0) + delta)), 2)


def _evento(estado, tipo, lado, texto, jogador=None, extra=None):
    ev = {'min': minuto_texto(estado), 't': estado['minuto'], 'periodo': estado['periodo'], 'tipo': tipo, 'lado': lado,
          'texto': texto, 'jogador': jogador, 'placar': f"{estado['placar']['casa']}-{estado['placar']['fora']}"}
    if extra:
        ev.update(extra)
    estado['eventos'].append(ev)
    return ev


def _nome_time(estado, lado):
    l = estado['lados'][lado]
    return l.get('nome_time') or dados.obter(l['time'])['nome']


# ------------------------------------------------------------------ um minuto

def _finalizar(estado, rng, lado, rival, fa, fr, xi_a, xi_r, penalti=False):
    """ Resolve uma finalização do `lado` contra o goleiro do `rival`. Devolve True se foi gol. """
    st_a, st_r = estado['stats'][lado], estado['stats'][rival]
    l = estado['lados'][lado]
    campo = [j for j in xi_a if j['pos'] != 'GOL'] or xi_a
    if penalti:
        batedor = max(campo, key=lambda j: j['fin'])
    else:
        batedor = _escolhe(rng, campo, [PESO_FINALIZADOR[j['pos']] * (j['fin'] / 70) ** 2 for j in campo])
    goleiro = next((j for j in xi_r if j['pos'] == 'GOL'), None)
    nome_t, nome_r = _nome_time(estado, lado), _nome_time(estado, rival)
    st_a['chutes'] += 1

    if penalti:
        p_gol = 0.80 + (batedor['fin'] - fr['gol']) * 0.003
        p_gol = max(0.6, min(0.9, p_gol))
        st_a['no_alvo'] += 1
        if rng.random() < p_gol:
            return _gol(estado, rng, lado, batedor, None, nome_t, penalti=True)
        _nota(estado, batedor['nome'], -0.5)
        if goleiro:
            _nota(estado, goleiro['nome'], 1.0)
        st_r['defesas'] += 1
        _evento(estado, 'penalti_perdido', lado, narracao.penalti_perdido(rng, batedor['nome'], goleiro['nome'] if goleiro else '?'), batedor['nome'])
        return False

    p_alvo = max(0.28, min(0.62, 0.40 + (batedor['fin'] - 70) * 0.004))
    if rng.random() > p_alvo:
        _nota(estado, batedor['nome'], -0.05)
        if rng.random() < 0.30:
            st_a['escanteios'] += 1
        _evento(estado, 'fora', lado, narracao.chute_fora(rng, batedor['nome'], nome_r), batedor['nome'])
        return False
    st_a['no_alvo'] += 1
    conv = ESTILOS[l['estilo']]['conv']
    if estado['lados'][rival]['mentalidade'] in ('ofensivo', 'tudo') and l['estilo'] == 'contra':
        conv *= 1.08
    p_gol = (0.27 + (batedor['fin'] - fr['gol']) * 0.009) * conv
    p_gol = max(0.08, min(0.62, p_gol))
    if rng.random() < p_gol:
        return _gol(estado, rng, lado, batedor, xi_a, nome_t)
    st_r['defesas'] += 1
    if goleiro:
        _nota(estado, goleiro['nome'], 0.25)
    _nota(estado, batedor['nome'], 0.05)
    if rng.random() < 0.07:
        _evento(estado, 'trave', lado, narracao.trave(rng, batedor['nome']), batedor['nome'])
    else:
        st_a['escanteios'] += 1 if rng.random() < 0.35 else 0
        _evento(estado, 'defesa', rival, narracao.defesa(rng, goleiro['nome'] if goleiro else 'O goleiro', batedor['nome']),
                goleiro['nome'] if goleiro else None)
    return False


def _gol(estado, rng, lado, batedor, xi, nome_t, penalti=False):
    estado['placar'][lado] += 1
    assistente = None
    if xi and not penalti and rng.random() < 0.72:
        cand = [j for j in xi if j['nome'] != batedor['nome'] and j['pos'] != 'GOL']
        if cand:
            assistente = _escolhe(rng, cand, [(j['cri'] / 70) ** 2 * (1.5 if j['pos'] in ('MEI', 'PON') else 1.0) for j in cand])
    _nota(estado, batedor['nome'], 1.1 if not penalti else 0.8)
    if assistente:
        _nota(estado, assistente['nome'], 0.7)
    gols = sum(1 for e in estado['eventos'] if e['tipo'] == 'gol' and e['jogador'] == batedor['nome']) + 1
    _evento(estado, 'gol', lado, narracao.gol(rng, batedor['nome'], assistente['nome'] if assistente else None, nome_t,
                                              estado['placar']['casa'], estado['placar']['fora'], penalti, gols),
            batedor['nome'], {'assistencia': assistente['nome'] if assistente else None, 'penalti': penalti})
    return True


def simular_minuto(estado):
    """ Avança 1 minuto do relógio. Aplica a IA nos lados que não são do usuário. """
    p = estado['periodo']
    estado['minuto'] += 1
    rng = random.Random(f"{estado['seed']}-{p}-{estado['minuto']}")
    _ia(estado, rng)

    fc, xi_c = forca_lado(estado, 'casa')
    ff, xi_f = forca_lado(estado, 'fora')
    forcas = {'casa': (fc, xi_c), 'fora': (ff, xi_f)}
    ment = {l: MENTALIDADES[estado['lados'][l]['mentalidade']] for l in LADOS}
    est = {l: ESTILOS[estado['lados'][l]['estilo']] for l in LADOS}

    # posse
    pot = {l: (forcas[l][0]['cri'] * est[l]['posse'] * (1.03 if l == 'casa' else 1.0)) ** 3 for l in LADOS}
    share = {l: pot[l] / (pot['casa'] + pot['fora']) for l in LADOS}
    for l in LADOS:
        estado['stats'][l]['posse'] += share[l]

    for lado in LADOS:
        rival = 'fora' if lado == 'casa' else 'casa'
        fa, xi_a = forcas[lado]
        fr, xi_r = forcas[rival]
        p_ataque = BASE_ATAQUE * 2 * share[lado] * ment[lado]['ataque'] * ment[rival]['expo']
        if rng.random() < p_ataque:
            ratio = fa['atq'] / max(30, fr['def'])
            p_chute = max(0.30, min(0.90, 0.52 + 1.5 * (ratio - 1)))
            if rng.random() < p_chute:
                # falta dentro da área? vira pênalti
                if rng.random() < 0.035:
                    estado['stats'][rival]['faltas'] += 1
                    _evento(estado, 'penalti', lado, narracao.penalti(rng, _nome_time(estado, lado)), None)
                    _finalizar(estado, rng, lado, rival, fa, fr, xi_a, xi_r, penalti=True)
                else:
                    _finalizar(estado, rng, lado, rival, fa, fr, xi_a, xi_r)
            elif rng.random() < 0.45:
                _evento(estado, 'desarme', rival, narracao.desarme(rng, _nome_time(estado, rival)), None)

        # faltas / cartões
        p_falta = 0.15 * ment[lado]['faltas'] * est[lado]['faltas'] * (1 - share[lado] + 0.5)
        if rng.random() < p_falta:
            _falta(estado, rng, lado, xi_a)

        # lesão
        if rng.random() < 0.0006:
            _lesao(estado, rng, lado, xi_a)

    # expulsão direta (rara)
    for lado in LADOS:
        if rng.random() < 0.0009:
            _expulsar(estado, rng, lado, em_campo(estado, lado), direto=True)

    # enchimento de narrativa quando nada aconteceu há tempo
    if estado['minuto'] % 9 == 0 and not any(e['t'] >= estado['minuto'] - 3 and e['periodo'] == p for e in estado['eventos']):
        lider = 'casa' if share['casa'] >= share['fora'] else 'fora'
        _evento(estado, 'info', lider, narracao.posse(rng, _nome_time(estado, lider)), None)


def _falta(estado, rng, lado, xi):
    estado['stats'][lado]['faltas'] += 1
    campo = [j for j in xi if j['pos'] != 'GOL']
    autor = _escolhe(rng, campo, [PESO_FALTA[j['pos']] for j in campo])
    if rng.random() < 0.13:
        l = estado['lados'][lado]
        amarelos = l['amarelos'].get(autor['nome'], 0) + 1
        l['amarelos'][autor['nome']] = amarelos
        estado['stats'][lado]['amarelos'] += 1
        _nota(estado, autor['nome'], -0.3)
        if amarelos >= 2:
            _evento(estado, 'amarelo', lado, narracao.segundo_amarelo(rng, autor['nome']), autor['nome'])
            _expulsar(estado, rng, lado, xi, direto=False, nome=autor['nome'])
        else:
            _evento(estado, 'amarelo', lado, narracao.amarelo(rng, autor['nome'], _nome_time(estado, lado)), autor['nome'])


def _expulsar(estado, rng, lado, xi, direto, nome=None):
    campo = [j for j in xi if j['pos'] != 'GOL'] or xi
    j = next((x for x in xi if x['nome'] == nome), None) or _escolhe(rng, campo, [PESO_FALTA[x['pos']] for x in campo])
    l = estado['lados'][lado]
    if j['nome'] in l['expulsos']:
        return
    l['expulsos'].append(j['nome'])
    estado['stats'][lado]['vermelhos'] += 1
    _nota(estado, j['nome'], -1.5)
    _evento(estado, 'vermelho', lado, narracao.vermelho(rng, j['nome'], _nome_time(estado, lado), direto), j['nome'])


def _lesao(estado, rng, lado, xi):
    campo = [j for j in xi if j['pos'] != 'GOL']
    j = rng.choice(campo)
    l = estado['lados'][lado]
    l['lesionados'].append(j['nome'])
    _evento(estado, 'lesao', lado, narracao.lesao(rng, j['nome']), j['nome'])
    if l['subs'] < LIMITE_SUBS and l['banco'] and estado['usuario_lado'] != lado:
        _substituir(estado, lado, j['nome'], automatico=True)


def _substituir(estado, lado, sai, entra=None, automatico=False):
    """ Troca `sai` por `entra` (ou o melhor do banco na mesma posição). Devolve (ok, mensagem). """
    l = estado['lados'][lado]
    if l['subs'] >= LIMITE_SUBS:
        return False, 'Limite de 5 substituições atingido.'
    if sai not in l['titulares'] or sai in l['expulsos']:
        return False, 'Esse jogador não está em campo.'
    if entra is None:
        pos = _jogador(l, sai)['pos']
        cand = sorted((_jogador(l, n) for n in l['banco']),
                      key=lambda j: -(j['nota'] - dados.custo_posicao(j['pos'], pos)))
        if not cand:
            return False, 'Banco vazio.'
        entra = cand[0]['nome']
    if entra not in l['banco']:
        return False, 'Esse jogador não está no banco.'
    i = l['titulares'].index(sai)
    l['titulares'][i] = entra
    l['banco'].remove(entra)
    l['saiu'].append(sai)
    l['subs'] += 1
    estado['notas'].setdefault(entra, 6.0)
    _evento(estado, 'substituicao', lado, narracao.substituicao(random.Random(f"sub-{estado['seed']}-{estado['minuto']}-{sai}"),
                                                                entra, sai), entra, {'saiu': sai})
    return True, 'ok'


def _ia(estado, rng):
    """ O lado que não é do usuário ajusta mentalidade e faz trocas. """
    m = estado['minuto']
    for lado in LADOS:
        if estado['usuario_lado'] == lado:
            continue
        rival = 'fora' if lado == 'casa' else 'casa'
        l = estado['lados'][lado]
        saldo = estado['placar'][lado] - estado['placar'][rival]
        if m in (46, 60, 70, 78, 84):
            ant = l['mentalidade']
            if saldo < 0 and m >= 60:
                l['mentalidade'] = 'tudo' if (saldo <= -2 or m >= 78) else 'ofensivo'
            elif saldo >= 2 and m >= 60:
                l['mentalidade'] = 'retranca'
            elif saldo == 1 and m >= 75:
                l['mentalidade'] = 'retranca'
            elif saldo == 0 and m >= 70 and l['mentalidade'] == 'retranca':
                l['mentalidade'] = 'equilibrado'
            if l['mentalidade'] != ant:
                _evento(estado, 'tatica', lado, narracao.tatica(rng, _nome_time(estado, lado), MENTALIDADES[l['mentalidade']]['nome']), None)
        if m in (62, 72, 80) and l['subs'] < LIMITE_SUBS and l['banco']:
            em = em_campo(estado, lado)
            cansados = [j for j in em if j['pos'] != 'GOL']
            if cansados:
                sai = min(cansados, key=lambda j: j['nota'] + estado['notas'].get(j['nome'], 6) * 2)
                _substituir(estado, lado, sai['nome'], automatico=True)


# ------------------------------------------------------------------ controle da partida

def aplicar_ajuste(estado, lado, ajuste):
    """ Ajustes do técnico: {'mentalidade','estilo'} e/ou {'sai','entra'}. Devolve (ok, mensagem). """
    if estado['status'] == 'fim':
        return False, 'A partida já acabou.'
    l = estado['lados'][lado]
    rng = random.Random(f"aj-{estado['seed']}-{estado['minuto']}")
    if 'mentalidade' in ajuste:
        if ajuste['mentalidade'] not in MENTALIDADES:
            return False, 'Mentalidade inválida.'
        if ajuste['mentalidade'] != l['mentalidade']:
            l['mentalidade'] = ajuste['mentalidade']
            _evento(estado, 'tatica', lado, narracao.tatica(rng, _nome_time(estado, lado), MENTALIDADES[l['mentalidade']]['nome']), None)
    if 'estilo' in ajuste:
        if ajuste['estilo'] not in ESTILOS:
            return False, 'Estilo inválido.'
        l['estilo'] = ajuste['estilo']
    if ajuste.get('sai'):
        return _substituir(estado, lado, ajuste['sai'], ajuste.get('entra') or None)
    return True, 'ok'


def avancar(estado, ate='fim', maximo_minutos=None):
    """
    Simula até `ate`: 'intervalo' | 'fim' | número do minuto (1–90). Pausa sempre no intervalo.
    Devolve a lista de eventos novos.
    """
    if estado['status'] == 'fim':
        return []
    inicio = len(estado['eventos'])
    if estado['status'] in ('pre', 'intervalo'):
        if estado['status'] == 'intervalo':
            estado['periodo'] = 2
            estado['minuto'] = 45
            _evento(estado, 'info', None, narracao.inicio_segundo_tempo(random.Random(estado['seed'])), None)
        else:
            _evento(estado, 'info', None, narracao.apito_inicial(random.Random(estado['seed']), _nome_time(estado, 'casa'), _nome_time(estado, 'fora')), None)
        estado['status'] = 'jogando'
    passos = 0
    while True:
        p = estado['periodo']
        limite = (45 if p == 1 else 90) + estado['acrescimo'][str(p)]
        if estado['minuto'] >= limite:
            break
        simular_minuto(estado)
        passos += 1
        if isinstance(ate, int) and estado['minuto'] >= ate and estado['minuto'] < limite:
            return estado['eventos'][inicio:]
        if maximo_minutos and passos >= maximo_minutos:
            return estado['eventos'][inicio:]
    if estado['periodo'] == 1:
        estado['status'] = 'intervalo'
        _evento(estado, 'intervalo', None, narracao.intervalo(_nome_time(estado, 'casa'), _nome_time(estado, 'fora'),
                                                              estado['placar']['casa'], estado['placar']['fora']), None)
    else:
        estado['status'] = 'fim'
        _evento(estado, 'fim', None, narracao.fim_de_jogo(_nome_time(estado, 'casa'), _nome_time(estado, 'fora'),
                                                          estado['placar']['casa'], estado['placar']['fora']), None)
        if estado.get('mata_mata') and estado['placar']['casa'] == estado['placar']['fora']:
            decidir_penaltis(estado)
    return estado['eventos'][inicio:]


def decidir_penaltis(estado):
    """ Disputa de pênaltis: 5 cobranças alternadas (para antes se já decidiu) e depois morte súbita. """
    rng = random.Random(f"pen-{estado['seed']}")
    placar = {'casa': 0, 'fora': 0}
    cobrancas = {'casa': 0, 'fora': 0}
    batedores, goleiros = {}, {}
    for lado in LADOS:
        xi = [j for j in em_campo(estado, lado) if j['pos'] != 'GOL']
        batedores[lado] = sorted(xi, key=lambda j: -j['fin'])
        goleiros[lado] = next((j for j in em_campo(estado, lado) if j['pos'] == 'GOL'), None)
    _evento(estado, 'info', None, narracao.disputa_penaltis(), None)

    def bater(lado):
        rival = 'fora' if lado == 'casa' else 'casa'
        lista = batedores[lado]
        b = lista[cobrancas[lado] % len(lista)]
        cobrancas[lado] += 1
        gk = goleiros[rival]['gol'] if goleiros[rival] else 40
        p = max(0.55, min(0.93, 0.78 + (b['fin'] - gk) * 0.003))
        gol = rng.random() < p
        if gol:
            placar[lado] += 1
        _nota(estado, b['nome'], 0.3 if gol else -0.4)
        _evento(estado, 'pen_gol' if gol else 'pen_erro', lado, narracao.cobranca(rng, b['nome'], gol, placar['casa'], placar['fora']),
                b['nome'], {'penaltis': f"{placar['casa']}-{placar['fora']}"})

    decidido = False
    for rodada in range(5):
        for lado in LADOS:
            bater(lado)
            restantes = {l: 5 - cobrancas[l] for l in LADOS}
            if placar['casa'] > placar['fora'] + restantes['fora'] or placar['fora'] > placar['casa'] + restantes['casa']:
                decidido = True
                break
        if decidido:
            break
    extras = 0
    while not decidido:
        for lado in LADOS:
            bater(lado)
        if placar['casa'] != placar['fora']:
            decidido = True
        extras += 1
        if extras > 15 and not decidido:
            placar['casa' if rng.random() < 0.5 else 'fora'] += 1
            decidido = True
    vencedor = 'casa' if placar['casa'] > placar['fora'] else 'fora'
    estado['penaltis'] = {'casa': placar['casa'], 'fora': placar['fora'], 'vencedor': vencedor}
    _evento(estado, 'fim', vencedor, narracao.vencedor_penaltis(_nome_time(estado, vencedor), placar['casa'], placar['fora']), None)


def vencedor(estado):
    """ 'casa' | 'fora' | None (empate sem pênaltis). """
    p = estado['placar']
    if p['casa'] != p['fora']:
        return 'casa' if p['casa'] > p['fora'] else 'fora'
    return (estado.get('penaltis') or {}).get('vencedor')


def simular_completo(estado):
    """ Joga a partida inteira (os dois tempos) com as IAs. """
    while estado['status'] != 'fim':
        avancar(estado, 'fim')
    return estado


def resumo(estado):
    """ Estatísticas finais prontas para exibir. """
    total_posse = estado['stats']['casa']['posse'] + estado['stats']['fora']['posse'] or 1
    stats = {}
    for l in LADOS:
        s = dict(estado['stats'][l])
        s['posse'] = round(100 * s['posse'] / total_posse)
        stats[l] = s
    melhor = max(estado['notas'].items(), key=lambda kv: kv[1]) if estado['notas'] else None
    return {'placar': estado['placar'], 'stats': stats, 'craque': melhor[0] if melhor else None,
            'nota_craque': melhor[1] if melhor else None}


def simular_rapido(chave_casa, chave_fora, seed):
    """ Resultado de uma partida entre IAs (usado na temporada). Devolve o estado final. """
    estado = novo_estado({'time': chave_casa}, {'time': chave_fora}, seed, usuario_lado=None)
    return simular_completo(estado)

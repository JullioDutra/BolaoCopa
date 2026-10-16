"""
Campanha do Cabeçudos: 8 rivais, do campinho de várzea à final. Cada um é um bot com "personalidade":
vel (velocidade relativa ao jogador), pulo (chance de pular na bola alta), reacao (atraso em segundos),
chute (força), erro (chance de errar o tempo da jogada), ousadia (quanto avança para atacar).
"""
DURACAO_S = 60          # tempo regulamentar de cada partida
TOLERANCIA_S = 4        # relógio do navegador x servidor
MAX_GOLS = 25

FASES = [
    {'nome': 'Zé da Várzea', 'palco': 'Campinho do bairro', 'cor': '#64748b', 'pele': '#c68642',
     'vel': 0.55, 'pulo': 0.25, 'reacao': 0.55, 'chute': 0.65, 'erro': 0.40, 'ousadia': 0.30},
    {'nome': 'Tonhão', 'palco': 'Série D', 'cor': '#78350f', 'pele': '#8d5524',
     'vel': 0.65, 'pulo': 0.35, 'reacao': 0.45, 'chute': 0.75, 'erro': 0.32, 'ousadia': 0.40},
    {'nome': 'Bigode Veloz', 'palco': 'Série C', 'cor': '#0e7490', 'pele': '#e0ac69',
     'vel': 0.75, 'pulo': 0.45, 'reacao': 0.36, 'chute': 0.82, 'erro': 0.25, 'ousadia': 0.45},
    {'nome': 'Paredão', 'palco': 'Série B', 'cor': '#4338ca', 'pele': '#f1c27d',
     'vel': 0.80, 'pulo': 0.65, 'reacao': 0.28, 'chute': 0.80, 'erro': 0.20, 'ousadia': 0.25},
    {'nome': 'Canhota de Ouro', 'palco': 'Série A', 'cor': '#be123c', 'pele': '#c68642',
     'vel': 0.88, 'pulo': 0.60, 'reacao': 0.22, 'chute': 0.95, 'erro': 0.15, 'ousadia': 0.60},
    {'nome': 'El Matador', 'palco': 'Libertadores', 'cor': '#0369a1', 'pele': '#e0ac69',
     'vel': 0.95, 'pulo': 0.70, 'reacao': 0.17, 'chute': 1.00, 'erro': 0.11, 'ousadia': 0.65},
    {'nome': 'Herr Muralha', 'palco': 'Semifinal mundial', 'cor': '#111827', 'pele': '#ffdbac',
     'vel': 1.00, 'pulo': 0.82, 'reacao': 0.12, 'chute': 1.05, 'erro': 0.07, 'ousadia': 0.55},
    {'nome': 'O Fenômeno', 'palco': 'Final do mundial', 'cor': '#ca8a04', 'pele': '#8d5524',
     'vel': 1.06, 'pulo': 0.88, 'reacao': 0.08, 'chute': 1.12, 'erro': 0.04, 'ousadia': 0.75},
]


def premio(fase, status):
    if status != 'vitoria':
        return 0
    return 3 + fase * 2 + (30 if fase == len(FASES) else 0)

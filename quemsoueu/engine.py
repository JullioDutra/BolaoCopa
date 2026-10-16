"""
Regras do "Quem Sou Eu?": craque do dia, perguntas rápidas (respondidas pela ficha), dicas, palpite e pontuação.
A IA só entra nas perguntas livres (ver servico.py); aqui tudo é determinístico.
"""
import hashlib
import random
import unicodedata

from .craques import CRAQUES

MAX_PERGUNTAS = 20
MAX_PALPITES = 3
PONTOS_BASE = 100
CUSTO_PERGUNTA = 4
CUSTO_PALPITE_ERRADO = 10
CUSTO_DICA = 8
PONTOS_MINIMOS = 10

RESPOSTAS = {'sim': 'Sim', 'nao': 'Não', 'talvez': 'Mais ou menos', 'nao_sei': 'Não sei dizer',
             'invalida': 'Pergunte algo de sim ou não'}

PAISES_EUROPA = {'Portugal', 'França', 'Holanda', 'Alemanha', 'Itália', 'Espanha', 'Croácia', 'Noruega', 'Polônia',
                 'Bélgica', 'Inglaterra'}
CLUBES_EUROPEUS = {
    'PSV', 'Barcelona', 'Valencia', 'Inter de Milão', 'Real Madrid', 'Milan', 'PSG', 'Udinese', 'Fiorentina',
    'Deportivo La Coruña', 'Olympiacos', 'Zaragoza', 'Roma', 'Fenerbahçe', 'Parma', 'Galatasaray', 'Porto', 'Zenit',
    'Benfica', 'Napoli', 'Sevilla', 'Sporting', 'Manchester United', 'Juventus', 'Cannes', 'Bordeaux', 'Ajax',
    'Feyenoord', 'Bayern de Munique', 'Hamburgo', 'Monaco', 'Molde', 'Red Bull Salzburg', 'Borussia Dortmund',
    'Manchester City', 'Arsenal', 'Brescia', 'Dinamo Zagreb', 'Tottenham', 'Basel', 'Chelsea', 'Liverpool',
    'Lech Poznań', 'Atlético de Madrid', 'Genk', 'Wolfsburg', 'Umeå', 'Rosengård',
}
CLUBES_BRASILEIROS = {
    'Santos', 'Botafogo', 'Corinthians', 'Flamengo', 'Botafogo-SP', 'Vasco', 'Fluminense', 'Cruzeiro', 'Grêmio',
    'Atlético-MG', 'São Paulo', 'Mogi Mirim', 'Palmeiras', 'Internacional', 'América-MG', 'Vitória',
}

# perguntas rápidas: (id, texto, função(ficha) -> 'sim' | 'nao')
RAPIDAS = [
    ('brasileiro', 'É brasileiro(a)?', lambda c: c['pais'] == 'Brasil'),
    ('sul_americano', 'É sul-americano(a)?', lambda c: c['pais'] in ('Brasil', 'Argentina', 'Uruguai')),
    ('europeu', 'É europeu(eia)?', lambda c: c['pais'] in PAISES_EUROPA),
    ('goleiro', 'É goleiro(a)?', lambda c: c['posicao'] == 'Goleiro'),
    ('defensor', 'É defensor (zagueiro ou lateral)?', lambda c: c['posicao'] in ('Zagueiro', 'Lateral')),
    ('meia', 'É meio-campista?', lambda c: c['posicao'] in ('Meia', 'Volante')),
    ('atacante', 'É atacante?', lambda c: c['posicao'] == 'Atacante'),
    ('aposentado', 'Já se aposentou?', lambda c: c['aposentado']),
    ('copa', 'Foi campeão(ã) do mundo pela seleção?', lambda c: c['copas'] > 0),
    ('bola_ouro', 'Ganhou a Bola de Ouro?', lambda c: c['bolas_de_ouro'] > 0),
    ('canhoto', 'É canhoto(a)?', lambda c: c['pe'] == 'esquerdo'),
    ('antes_1980', 'Nasceu antes de 1980?', lambda c: c['nascimento'] < 1980),
    ('europa', 'Jogou por clube europeu?', lambda c: any(cl in CLUBES_EUROPEUS for cl in c['clubes'])),
    ('clube_br', 'Jogou por clube brasileiro?', lambda c: any(cl in CLUBES_BRASILEIROS for cl in c['clubes'])),
]
RAPIDAS_POR_ID = {r[0]: r for r in RAPIDAS}

DICAS = [
    ('posicao', lambda c: f"Posição: {c['posicao']}"),
    ('pais', lambda c: f"Seleção: {c['pais']}"),
    ('decada', lambda c: f"Nasceu nos anos {c['nascimento'] // 10 * 10}"),
    ('clube', lambda c: f"Um dos clubes: {c['clubes'][len(c['clubes']) // 2]}"),
    ('fato', lambda c: f"Curiosidade: {c['curiosidades'][0]}"),
]


def normalizar(texto):
    sem_acento = unicodedata.normalize('NFKD', str(texto or '')).encode('ascii', 'ignore').decode()
    return ' '.join(''.join(ch if ch.isalnum() else ' ' for ch in sem_acento.lower()).split())


def craque_do_dia(dia):
    """ O mesmo craque para todo mundo no mesmo dia, sem repetir dentro de um ciclo da lista. """
    ciclo, pos = divmod(dia.toordinal(), len(CRAQUES))
    ordem = list(range(len(CRAQUES)))
    random.Random(int(hashlib.sha256(f'qse:{ciclo}'.encode()).hexdigest(), 16)).shuffle(ordem)
    return CRAQUES[ordem[pos]]


def craque_aleatorio(rng, evitar=()):
    opcoes = [c for c in CRAQUES if c['chave'] not in set(evitar)] or CRAQUES
    return rng.choice(opcoes)


def responder_rapida(ficha, rapida_id):
    _, texto, regra = RAPIDAS_POR_ID[rapida_id]
    return texto, ('sim' if regra(ficha) else 'nao')


def dica(ficha, n):
    """ n-ésima dica (0..). None quando acabaram. """
    if n >= len(DICAS):
        return None
    return DICAS[n][1](ficha)


def acertou(ficha, palpite):
    p = normalizar(palpite)
    if len(p) < 3:
        return False
    alvos = {normalizar(ficha['nome'])} | {normalizar(a) for a in ficha['apelidos']}
    if p in alvos:
        return True
    # sobrenome/nome marcante sozinho ("messi", "cruyff"), desde que não seja um nome comum demais
    tokens = normalizar(ficha['nome']).split()
    return len(tokens) > 1 and p == tokens[-1] and len(p) >= 5


def tokens_proibidos(ficha):
    """ Pedaços do nome que nunca podem aparecer num comentário da IA. """
    partes = set()
    for nome in [ficha['nome']] + ficha['apelidos']:
        for t in normalizar(nome).split():
            if len(t) >= 4 and t not in {'junior', 'silva', 'santos', 'jogador'}:
                partes.add(t)
    return partes


def comentario_seguro(ficha, comentario):
    c = normalizar(comentario)
    if not c or any(t in c.split() for t in tokens_proibidos(ficha)):
        return ''
    return str(comentario).strip()[:120]


def pontuar(perguntas, palpites_errados, dicas):
    return max(PONTOS_MINIMOS, PONTOS_BASE - CUSTO_PERGUNTA * perguntas - CUSTO_PALPITE_ERRADO * palpites_errados
               - CUSTO_DICA * dicas)


def premio(pontos):
    return pontos // 10


def ficha_para_ia(ficha):
    """ Ficha em texto para o prompt (inclui o nome: a IA precisa saber quem é, e nunca dizer). """
    copa = f"{ficha['copas']} título(s) de Copa do Mundo pela seleção" if ficha['copas'] else 'Nunca ganhou Copa do Mundo'
    bola = f"{ficha['bolas_de_ouro']} Bola(s) de Ouro" if ficha['bolas_de_ouro'] else 'Nunca ganhou a Bola de Ouro'
    return '\n'.join([
        f"Nome: {ficha['nome']} (também conhecido como: {', '.join(ficha['apelidos'])})",
        f"Gênero: {'feminino' if ficha['genero'] == 'F' else 'masculino'}",
        f"Seleção: {ficha['pais']}", f"Posição: {ficha['posicao']}", f"Nascimento: {ficha['nascimento']}",
        f"Situação: {'aposentado' if ficha['aposentado'] else 'em atividade'}",
        f"Principais clubes: {', '.join(ficha['clubes'])}", copa, bola, f"Pé preferido: {ficha['pe']}",
        'Curiosidades: ' + '; '.join(ficha['curiosidades']),
    ])


def emojis(perguntas):
    cor = {'sim': '🟩', 'nao': '🟥', 'talvez': '🟨'}
    return ''.join(cor.get(p['resposta'], '⬜') for p in perguntas)

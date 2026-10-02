"""
Cliente enxuto da API football-data.org (plano gratuito cobre o Brasileirão, código "BSA").

  * Cadastre-se em https://www.football-data.org/client/register e coloque o token
    na variável de ambiente FOOTBALL_DATA_TOKEN (no PythonAnywhere: arquivo .env).
  * Usa só a biblioteca padrão (urllib), então não precisa instalar nada.
  * Plano gratuito: 10 requisições/minuto — por isso tudo aqui é cacheado.

No PythonAnywhere GRATUITO só dá para acessar sites da lista de liberados
(https://www.pythonanywhere.com/whitelist/); confira se api.football-data.org está
lá. Em contas pagas não há essa restrição.
"""
import json
import logging
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

BASE_URL = 'https://api.football-data.org/v4'
COMPETICAO_PADRAO = 'BSA'  # Campeonato Brasileiro Série A
NOMES_COMPETICAO = {'BSA': 'Brasileirão Série A', 'BSB': 'Brasileirão Série B', 'CLI': 'Libertadores'}


class ApiIndisponivel(Exception):
    """ Token ausente, rede bloqueada, limite estourado ou resposta inválida. """


# Trechos (já normalizados) dos nomes que a API usa -> nome do Clube no nosso banco.
# A ordem importa: "athletico" precisa vir antes de qualquer teste por "atletico".
_ALIASES = [
    ('mineiro', 'Atlético-MG'), ('atletico-mg', 'Atlético-MG'), ('atletico mg', 'Atlético-MG'),
    ('athletico', 'Athletico-PR'), ('paranaense', 'Athletico-PR'),
    ('flamengo', 'Flamengo'), ('palmeiras', 'Palmeiras'), ('corinthians', 'Corinthians'),
    ('sao paulo', 'São Paulo'), ('santos', 'Santos'), ('vasco', 'Vasco'),
    ('botafogo', 'Botafogo'), ('fluminense', 'Fluminense'), ('gremio', 'Grêmio'),
    ('internacional', 'Internacional'), ('cruzeiro', 'Cruzeiro'), ('bahia', 'Bahia'),
    ('vitoria', 'Vitória'), ('bragantino', 'Bragantino'), ('mirassol', 'Mirassol'),
    ('coritiba', 'Coritiba'), ('chapecoense', 'Chapecoense'), ('remo', 'Remo'),
]


def _normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto or '').encode('ascii', 'ignore').decode('ascii')
    return texto.strip().lower()


def nome_canonico(time_api):
    """ Converte o time da API ({'name','shortName','tla'}) no nome usado no nosso banco. """
    candidatos = [time_api.get('shortName'), time_api.get('name')]
    for texto in candidatos:
        norm = _normalizar(texto)
        for trecho, nome in _ALIASES:
            if trecho in norm:
                return nome
    return (time_api.get('shortName') or time_api.get('name') or '?').strip()


def _token():
    token = getattr(settings, 'FOOTBALL_DATA_TOKEN', None)
    if not token:
        raise ApiIndisponivel("FOOTBALL_DATA_TOKEN não configurado.")
    return token


def _get(caminho, params=None, timeout=10):
    url = f"{BASE_URL}{caminho}"
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'X-Auth-Token': _token(), 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as erro:
        raise ApiIndisponivel(f"A API respondeu HTTP {erro.code} em {caminho}.") from erro
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as erro:
        raise ApiIndisponivel(f"Falha ao acessar a API: {erro}") from erro


def _normalizar_partida(m):
    placar = (m.get('score') or {}).get('fullTime') or {}
    return {
        'external_id': m['id'],
        'data_hora': m['utcDate'],  # ISO 8601 em UTC ("2026-04-12T21:00:00Z")
        'status': m.get('status', ''),
        'rodada': m.get('matchday'),
        'casa': nome_canonico(m['homeTeam']),
        'fora': nome_canonico(m['awayTeam']),
        'escudo_casa': m['homeTeam'].get('crest') or '',
        'escudo_fora': m['awayTeam'].get('crest') or '',
        'gols_casa': placar.get('home'),
        'gols_fora': placar.get('away'),
    }


def partidas(competicao=COMPETICAO_PADRAO, rodada=None, status=None):
    """ Lista de partidas normalizadas (dicts). Sem cache: quem chama decide a frequência. """
    params = {}
    if rodada:
        params['matchday'] = rodada
    if status:
        params['status'] = status
    dados = _get(f'/competitions/{competicao}/matches', params)
    return [_normalizar_partida(m) for m in dados.get('matches', [])]


def rodada_atual(competicao=COMPETICAO_PADRAO):
    dados = _get(f'/competitions/{competicao}')
    return ((dados.get('currentSeason') or {}).get('currentMatchday')) or None


def classificacao(competicao=COMPETICAO_PADRAO, cache_segundos=1800):
    """ Tabela do campeonato (cacheada). Devolve [] se a API estiver fora do ar. """
    chave = f'tabela:{competicao}'
    tabela = cache.get(chave)
    if tabela is not None:
        return tabela
    try:
        dados = _get(f'/competitions/{competicao}/standings')
    except ApiIndisponivel as erro:
        logger.warning("Classificação indisponível: %s", erro)
        return cache.get(chave + ':antiga') or []

    total = next((s for s in dados.get('standings', []) if s.get('type') == 'TOTAL'), None)
    tabela = []
    for linha in (total or {}).get('table', []):
        tabela.append({
            'posicao': linha['position'],
            'time': nome_canonico(linha['team']),
            'escudo': linha['team'].get('crest') or '',
            'pontos': linha['points'],
            'jogos': linha['playedGames'],
            'vitorias': linha['won'],
            'saldo': linha['goalDifference'],
        })
    cache.set(chave, tabela, cache_segundos)
    cache.set(chave + ':antiga', tabela, 60 * 60 * 24 * 7)  # reserva para quando a API cair
    return tabela

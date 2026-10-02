"""API-Football (api-sports.io): plano grátis = 100 req/dia. Tem previsão de resultado, lesões e artilharia."""
from django.conf import settings

from palpites.api_futebol import nome_canonico

from ..posicoes import mapear_posicao
from .base import ProvedorIndisponivel, http_get_json

BASE = 'https://v3.football.api-sports.io'
NOME = 'api-football'
LIGA_BRASILEIRAO = 71


def disponivel():
    return bool(getattr(settings, 'APIFOOTBALL_KEY', None))


def _get(caminho, params=None, cache_segundos=0):
    if not disponivel():
        raise ProvedorIndisponivel("APIFOOTBALL_KEY não configurada.")
    dados = http_get_json(BASE + caminho, params, {'x-apisports-key': settings.APIFOOTBALL_KEY}, cache_segundos=cache_segundos)
    erros = dados.get('errors')
    if erros:
        raise ProvedorIndisponivel(f"API-Football: {erros}")
    return dados.get('response') or []


def buscar_times(nome):
    saida = []
    for item in _get('/teams', {'search': nome}, cache_segundos=24 * 3600):
        t, v = item.get('team') or {}, item.get('venue') or {}
        saida.append({'fonte': NOME, 'id': t.get('id'), 'nome': t.get('name') or '?', 'curto': t.get('code') or '',
                      'sigla': t.get('code') or '', 'pais': t.get('country') or '', 'cidade': v.get('city') or '',
                      'estadio': v.get('name') or '', 'fundacao': t.get('founded'), 'escudo': t.get('logo') or '', 'cor': ''})
    return saida


def elenco(id_time):
    resp = _get('/players/squads', {'team': id_time}, cache_segundos=24 * 3600)
    jogadores = (resp[0].get('players') if resp else None) or []
    return [{'fonte': NOME, 'id': j.get('id'), 'nome': j.get('name') or '?', 'posicao': mapear_posicao(j.get('position')),
             'detalhe': j.get('position') or '', 'numero': j.get('number'), 'nascimento': None, 'nacionalidade': '',
             'foto': j.get('photo') or ''} for j in jogadores]


def lesoes(temporada, liga=LIGA_BRASILEIRAO):
    """ {nome do time: [{'jogador','motivo'}]} com os desfalques conhecidos. """
    saida = {}
    for item in _get('/injuries', {'league': liga, 'season': temporada}, cache_segundos=3 * 3600):
        time = nome_canonico({'name': (item.get('team') or {}).get('name')})
        j = item.get('player') or {}
        lista = saida.setdefault(time, [])
        if not any(x['jogador'] == j.get('name') for x in lista):
            lista.append({'jogador': j.get('name') or '?', 'motivo': j.get('reason') or j.get('type') or ''})
    return saida


def artilheiros(temporada, liga=LIGA_BRASILEIRAO, limite=10):
    saida = []
    for item in _get('/players/topscorers', {'league': liga, 'season': temporada}, cache_segundos=3600)[:limite]:
        p = item.get('player') or {}
        est = (item.get('statistics') or [{}])[0]
        saida.append({'jogador': p.get('name') or '?', 'time': nome_canonico({'name': (est.get('team') or {}).get('name')}),
                      'escudo': (est.get('team') or {}).get('logo') or '', 'gols': (est.get('goals') or {}).get('total') or 0,
                      'assistencias': (est.get('goals') or {}).get('assists') or 0, 'jogos': (est.get('games') or {}).get('appearences') or 0})
    return saida


def previsao_do_jogo(casa, fora, data_iso, temporada, liga=LIGA_BRASILEIRAO):
    """ Procura o jogo na data e devolve a previsão {'casa','empate','fora','conselho'} ou None. """
    jogos = _get('/fixtures', {'league': liga, 'season': temporada, 'date': data_iso}, cache_segundos=6 * 3600)
    alvo = next((j for j in jogos
                 if nome_canonico({'name': j['teams']['home']['name']}) == casa
                 and nome_canonico({'name': j['teams']['away']['name']}) == fora), None)
    if not alvo:
        return None
    resp = _get('/predictions', {'fixture': alvo['fixture']['id']}, cache_segundos=6 * 3600)
    if not resp:
        return None
    pred = resp[0].get('predictions') or {}
    pct = pred.get('percent') or {}

    def num(v):
        try:
            return int(str(v).rstrip('%'))
        except (TypeError, ValueError):
            return None
    return {'casa': num(pct.get('home')), 'empate': num(pct.get('draw')), 'fora': num(pct.get('away')),
            'conselho': pred.get('advice') or ''}

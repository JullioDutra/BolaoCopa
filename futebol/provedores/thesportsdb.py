"""TheSportsDB (chave pública de testes "3" funciona para consultas básicas; chave própria é paga)."""
from django.conf import settings

from ..posicoes import mapear_posicao
from .base import http_get_json

NOME = 'thesportsdb'


def disponivel():
    return True    # a chave de testes é pública


def _base():
    return f"https://www.thesportsdb.com/api/v1/json/{getattr(settings, 'THESPORTSDB_KEY', None) or '3'}"


def _time(t):
    return {
        'fonte': NOME, 'id': t.get('idTeam'), 'nome': t.get('strTeam') or '?', 'curto': t.get('strTeamShort') or '',
        'sigla': (t.get('strTeamShort') or '')[:6], 'pais': t.get('strCountry') or '', 'cidade': t.get('strLocation') or '',
        'estadio': t.get('strStadium') or '', 'fundacao': int(t['intFormedYear']) if (t.get('intFormedYear') or '').isdigit() else None,
        'escudo': t.get('strTeamBadge') or t.get('strBadge') or '', 'cor': t.get('strColour1') or '', 'liga': t.get('strLeague') or '',
    }


def buscar_times(nome):
    dados = http_get_json(f"{_base()}/searchteams.php", {'t': nome}, cache_segundos=24 * 3600)
    return [_time(t) for t in (dados.get('teams') or [])]


def _atleta(p):
    return {
        'fonte': NOME, 'id': p.get('idPlayer'), 'nome': p.get('strPlayer') or '?', 'posicao': mapear_posicao(p.get('strPosition')),
        'detalhe': p.get('strPosition') or '', 'numero': int(p['strNumber']) if (p.get('strNumber') or '').isdigit() else None,
        'nascimento': (p.get('dateBorn') or '')[:10] or None, 'nacionalidade': p.get('strNationality') or '',
        'foto': p.get('strCutout') or p.get('strThumb') or '', 'time_nome': p.get('strTeam') or '',
    }


def elenco(id_time):
    dados = http_get_json(f"{_base()}/lookup_all_players.php", {'id': id_time}, cache_segundos=24 * 3600)
    return [_atleta(p) for p in (dados.get('player') or [])]


def buscar_jogadores(nome):
    dados = http_get_json(f"{_base()}/searchplayers.php", {'p': nome}, cache_segundos=24 * 3600)
    return [_atleta(p) for p in (dados.get('player') or [])]

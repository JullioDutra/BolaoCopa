"""football-data.org (token grátis; Brasileirão Série A = BSA). Limite: 10 req/min."""
from django.conf import settings

from palpites.api_futebol import nome_canonico

from ..posicoes import mapear_posicao
from .base import ProvedorIndisponivel, http_get_json

BASE = 'https://api.football-data.org/v4'
NOME = 'football-data'


def disponivel():
    return bool(getattr(settings, 'FOOTBALL_DATA_TOKEN', None))


def _get(caminho, params=None, cache_segundos=0):
    if not disponivel():
        raise ProvedorIndisponivel("FOOTBALL_DATA_TOKEN não configurado.")
    return http_get_json(BASE + caminho, params, {'X-Auth-Token': settings.FOOTBALL_DATA_TOKEN}, cache_segundos=cache_segundos)


def _time(t, brasileiro=True):
    nome = nome_canonico(t) if brasileiro else (t.get('shortName') or t.get('name') or '?')
    return {
        'fonte': NOME, 'id': t.get('id'), 'nome': nome, 'curto': t.get('shortName') or '',
        'sigla': t.get('tla') or '', 'pais': (t.get('area') or {}).get('name', ''),
        'cidade': '', 'estadio': t.get('venue') or '', 'fundacao': t.get('founded'),
        'escudo': t.get('crest') or '', 'cor': '',
    }


def times_com_elenco(competicao='BSA'):
    """ [(time_dict, [atleta_dict])] — o elenco já vem no endpoint de times. """
    dados = _get(f'/competitions/{competicao}/teams', cache_segundos=6 * 3600)
    brasileiro = competicao.upper().startswith('BS')
    liga = (dados.get('competition') or {}).get('name', '')
    saida = []
    for t in dados.get('teams', []):
        time = _time(t, brasileiro)
        time['liga'] = liga
        atletas = [{
            'fonte': NOME, 'id': j.get('id'), 'nome': j.get('name', '?'), 'posicao': mapear_posicao(j.get('position')),
            'detalhe': j.get('position') or '', 'numero': j.get('shirtNumber'),
            'nascimento': (j.get('dateOfBirth') or '')[:10] or None, 'nacionalidade': j.get('nationality') or '', 'foto': '',
        } for j in t.get('squad', [])]
        saida.append((time, atletas))
    return saida


def artilheiros(competicao='BSA', limite=10):
    dados = _get(f'/competitions/{competicao}/scorers', {'limit': limite}, cache_segundos=3600)
    return [{
        'jogador': (s.get('player') or {}).get('name', '?'),
        'time': nome_canonico(s.get('team') or {}), 'escudo': (s.get('team') or {}).get('crest') or '',
        'gols': s.get('goals') or 0, 'assistencias': s.get('assists') or 0, 'jogos': s.get('playedMatches') or 0,
    } for s in dados.get('scorers', [])]


def _resultado(m, id_time):
    placar = (m.get('score') or {}).get('fullTime') or {}
    casa, fora = placar.get('home'), placar.get('away')
    if casa is None or fora is None:
        return None
    eh_casa = (m.get('homeTeam') or {}).get('id') == id_time
    pro, contra = (casa, fora) if eh_casa else (fora, casa)
    return {
        'data': (m.get('utcDate') or '')[:10], 'casa': nome_canonico(m['homeTeam']), 'fora': nome_canonico(m['awayTeam']),
        'placar': f"{casa} x {fora}", 'resultado': 'V' if pro > contra else 'D' if pro < contra else 'E',
    }


def ultimos_jogos(id_time, limite=5):
    dados = _get(f'/teams/{id_time}/matches', {'status': 'FINISHED', 'limit': limite}, cache_segundos=3600)
    jogos = [r for r in (_resultado(m, id_time) for m in dados.get('matches', [])) if r]
    return jogos[-limite:]


def confronto_direto(match_id, limite=6):
    dados = _get(f'/matches/{match_id}/head2head', {'limit': limite}, cache_segundos=6 * 3600)
    jogos = []
    for m in dados.get('matches', []):
        placar = (m.get('score') or {}).get('fullTime') or {}
        if placar.get('home') is None:
            continue
        jogos.append({'data': (m.get('utcDate') or '')[:10], 'casa': nome_canonico(m['homeTeam']),
                      'fora': nome_canonico(m['awayTeam']), 'placar': f"{placar['home']} x {placar['away']}",
                      'gols_casa': placar['home'], 'gols_fora': placar['away']})
    return jogos

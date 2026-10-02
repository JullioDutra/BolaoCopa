"""ESPN (API pública não documentada, sem chave): notícias com foto, placares ao vivo, times e elencos."""
from ..posicoes import mapear_posicao
from .base import http_get_json

NOME = 'espn'
LIGA_PADRAO = 'bra.1'


def disponivel():
    return True


def _base(liga):
    return f"https://site.api.espn.com/apis/site/v2/sports/soccer/{liga}"


def noticias(liga=LIGA_PADRAO, limite=8):
    dados = http_get_json(f"{_base(liga)}/news", {'lang': 'pt', 'region': 'br', 'limit': limite}, cache_segundos=1800)
    saida = []
    for a in dados.get('articles', []):
        link = (((a.get('links') or {}).get('web')) or {}).get('href') or ''
        if not link.lower().startswith(('http://', 'https://')):
            continue
        imagens = a.get('images') or []
        saida.append({'titulo': a.get('headline') or '', 'resumo': a.get('description') or '', 'link': link,
                      'imagem': (imagens[0].get('url') if imagens else '') or '', 'fonte': 'ESPN',
                      'publicado_em': a.get('published') or None})
    return [n for n in saida if n['titulo']][:limite]


def placar(liga=LIGA_PADRAO):
    """ Jogos do dia: [{'casa','fora','gols_casa','gols_fora','estado','detalhe'}] (estado: pre/in/post). """
    dados = http_get_json(f"{_base(liga)}/scoreboard", cache_segundos=60)
    jogos = []
    for ev in dados.get('events', []):
        comp = (ev.get('competitions') or [{}])[0]
        lados = {c.get('homeAway'): c for c in comp.get('competitors', [])}
        if 'home' not in lados or 'away' not in lados:
            continue
        status = (ev.get('status') or {}).get('type') or {}
        jogos.append({
            'id': ev.get('id'), 'casa': lados['home']['team'].get('displayName', '?'), 'fora': lados['away']['team'].get('displayName', '?'),
            'escudo_casa': lados['home']['team'].get('logo') or '', 'escudo_fora': lados['away']['team'].get('logo') or '',
            'gols_casa': lados['home'].get('score'), 'gols_fora': lados['away'].get('score'),
            'estado': status.get('state') or '', 'detalhe': status.get('shortDetail') or '', 'data': ev.get('date') or '',
        })
    return jogos


def times(liga=LIGA_PADRAO):
    dados = http_get_json(f"{_base(liga)}/teams", cache_segundos=24 * 3600)
    saida = []
    for esporte in dados.get('sports', []):
        for lg in esporte.get('leagues', []):
            for item in lg.get('teams', []):
                t = item.get('team') or {}
                logos = t.get('logos') or []
                saida.append({'fonte': NOME, 'id': t.get('id'), 'nome': t.get('displayName') or '?', 'curto': t.get('shortDisplayName') or '',
                              'sigla': t.get('abbreviation') or '', 'pais': '', 'cidade': t.get('location') or '', 'estadio': '',
                              'fundacao': None, 'escudo': (logos[0].get('href') if logos else '') or '',
                              'cor': ('#' + t['color']) if t.get('color') else '', 'liga': lg.get('name') or ''})
    return saida


def elenco(id_time, liga=LIGA_PADRAO):
    dados = http_get_json(f"{_base(liga)}/teams/{id_time}/roster", cache_segundos=24 * 3600)
    atletas = []
    for item in dados.get('athletes', []):
        grupo = item.get('items') if isinstance(item, dict) and 'items' in item else [item]   # plano ou agrupado
        atletas.extend(grupo)
    saida = []
    for a in atletas:
        pos = a.get('position') or {}
        saida.append({'fonte': NOME, 'id': a.get('id'), 'nome': a.get('fullName') or a.get('displayName') or '?',
                      'posicao': mapear_posicao(pos.get('abbreviation') or pos.get('displayName')),
                      'detalhe': pos.get('displayName') or '', 'numero': int(a['jersey']) if str(a.get('jersey') or '').isdigit() else None,
                      'nascimento': (a.get('dateOfBirth') or '')[:10] or None, 'nacionalidade': a.get('citizenship') or '',
                      'foto': (a.get('headshot') or {}).get('href') or ''})
    return saida

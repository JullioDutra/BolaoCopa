"""Importa estatísticas de jogadores (CSV ou API-Football) para o scout."""
import csv

from accounts.temas import normalizar

from .importar import Resumo, salvar_atleta, salvar_time
from .models import EstatisticaAtleta, Time
from .posicoes import mapear_posicao
from .provedores import api_football
from .provedores.base import ProvedorIndisponivel
from .scout import decimal_ou_none

COLUNAS_INT = ('jogos', 'minutos', 'gols', 'assistencias', 'amarelos', 'vermelhos', 'gols_sofridos', 'jogos_sem_sofrer', 'defesas')


def _int(v):
    try:
        return max(0, int(float(str(v).strip().replace(',', '.')))) if str(v).strip() else 0
    except ValueError:
        return 0


def _verdadeiro(v):
    return normalizar(str(v)) in ('1', 'sim', 's', 'true', 'x', 'yes')


def salvar_estatistica(d, fonte=''):
    """ d: nome, time, posicao, temporada, competicao + números. Cria time/atleta se preciso. """
    time, _ = salvar_time({'nome': d['time']}, fonte) if d.get('time') else (None, False)
    atleta, criado = salvar_atleta({'nome': d['nome'], 'posicao': d.get('posicao') or mapear_posicao(d.get('detalhe')),
                                    'detalhe': d.get('detalhe')}, time, fonte)
    if atleta is None:
        return None, False
    campos = {c: _int(d.get(c)) for c in COLUNAS_INT}
    campos.update(nota_media=decimal_ou_none(d.get('nota')), contratado=bool(d.get('contratado')),
                  valor_contratacao=_int(d.get('valor')) or None, fonte=fonte)
    est, novo = EstatisticaAtleta.objects.update_or_create(
        atleta=atleta, temporada=_int(d['temporada']), competicao=d.get('competicao') or 'Brasileirão Série A',
        time=time, defaults=campos)
    return est, novo


def importar_csv(caminho):
    """
    CSV: nome,time,posicao,temporada,competicao,jogos,minutos,gols,assistencias,amarelos,vermelhos,nota,
         gols_sofridos,jogos_sem_sofrer,defesas,contratado,valor
    """
    r = Resumo()
    with open(caminho, encoding='utf-8-sig', newline='') as f:
        for linha in csv.DictReader(f):
            if not (linha.get('nome') or '').strip() or not (linha.get('temporada') or '').strip():
                continue
            d = {k.strip().lower(): (v or '').strip() for k, v in linha.items() if k}
            d['contratado'] = _verdadeiro(d.get('contratado', ''))
            est, novo = salvar_estatistica(d, 'csv')
            if est is None:
                r['erros'].append(f"Posição desconhecida para {d['nome']} — preencha a coluna posicao.")
            else:
                r.contar(novo, 'atletas')
    return r


def importar_api_football(time, temporada, liga=api_football.LIGA_BRASILEIRAO, max_paginas=3):
    """ Estatísticas de um time na temporada (cada página = 1 requisição da cota diária). """
    r = Resumo()
    id_ext = time.ids_externos.get(api_football.NOME)
    if not id_ext:
        r['erros'].append(f"{time.nome} não tem id da API-Football. Rode: importar_futebol --fonte api-football --buscar \"{time.nome}\"")
        return r
    try:
        for pagina in range(1, max_paginas + 1):
            resp = api_football._get('/players', {'team': id_ext, 'season': temporada, 'league': liga, 'page': pagina},
                                     cache_segundos=12 * 3600)
            if not resp:
                break
            for item in resp:
                p = item.get('player') or {}
                s = (item.get('statistics') or [{}])[0]
                jogos, gols, cartoes = s.get('games') or {}, s.get('goals') or {}, s.get('cards') or {}
                est, novo = salvar_estatistica({
                    'nome': p.get('name') or '?', 'time': time.nome, 'detalhe': jogos.get('position') or '',
                    'temporada': temporada, 'competicao': (s.get('league') or {}).get('name') or 'Brasileirão Série A',
                    'jogos': jogos.get('appearences') or 0, 'minutos': jogos.get('minutes') or 0,
                    'gols': gols.get('total') or 0, 'assistencias': gols.get('assists') or 0,
                    'amarelos': cartoes.get('yellow') or 0, 'vermelhos': cartoes.get('red') or 0,
                    'nota': jogos.get('rating') or '', 'gols_sofridos': gols.get('conceded') or 0,
                    'defesas': gols.get('saves') or 0}, 'api-football')
                if est:
                    r.contar(novo, 'atletas')
            if len(resp) < 20:
                break
    except ProvedorIndisponivel as e:
        r['erros'].append(str(e))
    return r


def times_para_importar(nome=None):
    qs = Time.objects.all()
    if nome:
        qs = qs.filter(busca__contains=normalizar(nome))
    return [t for t in qs if t.ids_externos.get(api_football.NOME)]

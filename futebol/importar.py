"""
Importadores do banco de futebol (para pesquisa e comparativos).

Fontes:
  * internos  — reaproveita o que o site já tem: clubes do Bolão, jogadores da Seleção do Brasileirão
                e as cartas do Trunfo (com overall).
  * football-data / api-football / thesportsdb / espn — APIs (ver `provedores/`).
  * arquivo   — JSON ou CSV seu (ex.: exportado de Transfermarkt/Kaggle), para não depender de API.
"""
import csv
import json
from datetime import date

from accounts.temas import normalizar

from .models import Atleta, FonteAtleta, Time
from .posicoes import mapear_posicao
from .provedores import api_football, espn, football_data, thesportsdb
from .provedores.base import ProvedorIndisponivel

BUCKET_PT = {'Goleiro': 'GOL', 'Defensor': 'DEF', 'Meio-campista': 'MEI', 'Atacante': 'ATA'}


def _vazio(valor):
    return valor in (None, '', 0)


def salvar_time(d, fonte=''):
    """ Cria ou atualiza um Time a partir de um dict normalizado, sem apagar dados já preenchidos. """
    fonte = fonte or d.get('fonte', '')
    id_ext = d.get('id')
    time = None
    if fonte and id_ext is not None:
        time = next((t for t in Time.objects.all() if t.ids_externos.get(fonte) == id_ext), None)
    if time is None:
        chave = normalizar(d['nome'])
        time = next((t for t in Time.objects.filter(busca__contains=chave) if normalizar(t.nome) == chave), None)
    criado = time is None
    if criado:
        time = Time(nome=d['nome'])
    mapa = {'nome_curto': d.get('curto'), 'sigla': d.get('sigla'), 'pais': d.get('pais'), 'liga': d.get('liga'),
            'cidade': d.get('cidade'), 'estadio': d.get('estadio'), 'fundacao': d.get('fundacao'),
            'escudo_url': d.get('escudo'), 'cor': d.get('cor')}
    for campo, valor in mapa.items():
        if not _vazio(valor) and _vazio(getattr(time, campo)):
            setattr(time, campo, valor)
    if fonte and not time.fonte:
        time.fonte = fonte
    if fonte and id_ext is not None:
        time.ids_externos = {**time.ids_externos, fonte: id_ext}
    time.save()
    return time, criado


def salvar_atleta(d, time, fonte=''):
    fonte = fonte or d.get('fonte', '')
    posicao = d.get('posicao') or mapear_posicao(d.get('detalhe'))
    if not posicao:
        return None, False
    chave = normalizar(d['nome'])
    atleta = None
    if time is not None:
        atleta = next((a for a in Atleta.objects.filter(time=time) if a.busca == chave), None)
    if atleta is None and fonte and d.get('id') is not None:
        atleta = next((a for a in Atleta.objects.filter(busca=chave) if a.ids_externos.get(fonte) == d['id']), None)
    criado = atleta is None
    if criado:
        atleta = Atleta(nome=d['nome'], posicao=posicao, time=time)
    mapa = {'detalhe': d.get('detalhe'), 'numero': d.get('numero'), 'nacionalidade': d.get('nacionalidade'),
            'foto_url': d.get('foto'), 'overall': d.get('overall'), 'valor_mercado': d.get('valor_mercado')}
    for campo, valor in mapa.items():
        if not _vazio(valor) and _vazio(getattr(atleta, campo)):
            setattr(atleta, campo, valor)
    nasc = d.get('nascimento')
    if nasc and not atleta.nascimento:
        try:
            atleta.nascimento = nasc if isinstance(nasc, date) else date.fromisoformat(str(nasc)[:10])
        except ValueError:
            pass
    if not atleta.time_id and time is not None:
        atleta.time = time
    if fonte and not atleta.fonte:
        atleta.fonte = fonte
    if fonte and d.get('id') is not None:
        atleta.ids_externos = {**atleta.ids_externos, fonte: d['id']}
    atleta.save()
    return atleta, criado


class Resumo(dict):
    def __init__(self):
        super().__init__(times=0, atletas=0, atualizados=0, erros=[])

    def contar(self, criado, chave):
        if criado:
            self[chave] += 1
        else:
            self['atualizados'] += 1


def vincular(atleta, origem, ref_id):
    """ Registra de onde veio o atleta (idempotente) para o banco único apontar de volta aos jogos. """
    if atleta is not None:
        FonteAtleta.objects.get_or_create(origem=origem, ref_id=ref_id, defaults={'atleta': atleta})


def importar_internos():
    """ Aproveita os dados que o site já tem. Roda quantas vezes quiser (não duplica). """
    from convocacao.models import Jogador
    from duelos.models import CartaTrunfo
    from palpites.models import Clube

    r = Resumo()
    for clube in Clube.objects.all():
        liga = 'Brasileirão Série A' if clube.competicao == 'BRASILEIRAO' else 'Europa'
        time, criado = salvar_time({'nome': clube.nome, 'pais': 'Brasil' if clube.competicao == 'BRASILEIRAO' else '',
                                    'liga': liga, 'cor': clube.cor_hexadecimal}, 'interno')
        if time.clube_local_id is None:
            time.clube_local = clube
            time.save(update_fields=['clube_local'])
        r.contar(criado, 'times')

    for j in Jogador.objects.exclude(clube_atual__isnull=True).exclude(clube_atual=''):
        time, criado_t = salvar_time({'nome': j.clube_atual.strip()}, 'interno')
        r.contar(criado_t, 'times')
        atleta, criado = salvar_atleta({'nome': j.nome, 'posicao': BUCKET_PT.get(j.posicao, ''), 'detalhe': j.posicao}, time, 'interno')
        vincular(atleta, 'convocacao.Jogador', j.pk)
        if atleta is not None:
            if j.foto and not atleta.foto:
                atleta.foto = j.foto.name
                atleta.save(update_fields=['foto'])
            r.contar(criado, 'atletas')

    for carta in CartaTrunfo.objects.select_related('clube'):
        time, criado_t = salvar_time({'nome': carta.clube.nome}, 'interno')
        r.contar(criado_t, 'times')
        atleta, criado = salvar_atleta({'nome': carta.nome, 'posicao': mapear_posicao(carta.posicao), 'overall': carta.overall}, time, 'interno')
        vincular(atleta, 'duelos.CartaTrunfo', carta.pk)
        if atleta is not None:
            if atleta.overall is None:
                atleta.overall = carta.overall
                atleta.save(update_fields=['overall'])
            if carta.foto and not atleta.foto:
                atleta.foto = carta.foto.name
                atleta.save(update_fields=['foto'])
            r.contar(criado, 'atletas')

    # Draft/Mini-jogo: goleiros têm posição certa; jogadores de linha só se o atleta já existir (posição desconhecida)
    try:
        from minijogo.models import CartaJogador
        for c in CartaJogador.objects.select_related('elenco'):
            chave = normalizar(c.nome)
            atleta = next((a for a in Atleta.objects.filter(busca=chave)), None)
            if atleta is None and c.posicao == 'goleiro':
                atleta, criado = salvar_atleta({'nome': c.nome, 'posicao': 'GOL'}, None, 'interno')
                r.contar(criado, 'atletas')
            vincular(atleta, 'minijogo.CartaJogador', c.pk)
    except Exception as e:  # tabela ausente antes do migrate
        r['erros'].append(f'minijogo: {e}')
    return r


def importar_provedor(nome, competicao='BSA', liga_espn='bra.1', busca=None):
    """ Importa times (e elencos quando a fonte entrega) de uma API. Erros viram avisos no Resumo. """
    r = Resumo()
    try:
        if nome == 'football-data':
            for time_d, atletas in football_data.times_com_elenco(competicao):
                time, criado = salvar_time(time_d, nome)
                r.contar(criado, 'times')
                for a in atletas:
                    atleta, c = salvar_atleta(a, time, nome)
                    if atleta:
                        r.contar(c, 'atletas')
        elif nome == 'espn':
            for time_d in espn.times(liga_espn):
                time, criado = salvar_time(time_d, nome)
                r.contar(criado, 'times')
                try:
                    for a in espn.elenco(time_d['id'], liga_espn):
                        atleta, c = salvar_atleta(a, time, nome)
                        if atleta:
                            r.contar(c, 'atletas')
                except ProvedorIndisponivel as erro:
                    r['erros'].append(f"{time_d['nome']}: {erro}")
        elif nome in ('thesportsdb', 'api-football'):
            prov = thesportsdb if nome == 'thesportsdb' else api_football
            if not busca:
                raise ProvedorIndisponivel(f"Para {nome} informe --buscar \"nome do time\" (a busca gasta pouca cota).")
            for time_d in prov.buscar_times(busca):
                time, criado = salvar_time(time_d, nome)
                r.contar(criado, 'times')
                for a in prov.elenco(time_d['id']):
                    atleta, c = salvar_atleta(a, time, nome)
                    if atleta:
                        r.contar(c, 'atletas')
        else:
            raise ProvedorIndisponivel(f"Fonte desconhecida: {nome}")
    except ProvedorIndisponivel as erro:
        r['erros'].append(str(erro))
    return r


COLUNAS_CSV = ['time', 'pais', 'liga', 'jogador', 'posicao', 'numero', 'nascimento', 'nacionalidade', 'overall', 'valor_mercado']


def importar_arquivo(caminho):
    """
    JSON: {"times": [{"nome": "...", "pais": "...", "atletas": [{"nome": "...", "posicao": "Atacante", ...}]}]}
    CSV : colunas = time,pais,liga,jogador,posicao,numero,nascimento,nacionalidade,overall,valor_mercado
    """
    r = Resumo()
    if str(caminho).lower().endswith('.json'):
        with open(caminho, encoding='utf-8') as f:
            dados = json.load(f)
        for t in dados.get('times', []):
            time, criado = salvar_time({k: t.get(k) for k in ('nome', 'pais', 'liga', 'cidade', 'estadio', 'fundacao', 'escudo', 'cor')}
                                       | {'curto': t.get('nome_curto'), 'sigla': t.get('sigla')}, 'arquivo')
            r.contar(criado, 'times')
            for a in t.get('atletas', []):
                atleta, c = salvar_atleta(_atleta_de_arquivo(a), time, 'arquivo')
                if atleta:
                    r.contar(c, 'atletas')
    else:
        with open(caminho, encoding='utf-8-sig', newline='') as f:
            for linha in csv.DictReader(f):
                if not (linha.get('time') or '').strip() or not (linha.get('jogador') or '').strip():
                    continue
                time, criado = salvar_time({'nome': linha['time'].strip(), 'pais': linha.get('pais'), 'liga': linha.get('liga')}, 'arquivo')
                r.contar(criado, 'times')
                atleta, c = salvar_atleta(_atleta_de_arquivo({
                    'nome': linha['jogador'].strip(), 'posicao': linha.get('posicao'), 'numero': linha.get('numero'),
                    'nascimento': linha.get('nascimento'), 'nacionalidade': linha.get('nacionalidade'),
                    'overall': linha.get('overall'), 'valor_mercado': linha.get('valor_mercado')}), time, 'arquivo')
                if atleta:
                    r.contar(c, 'atletas')
    return r


def _inteiro(v):
    try:
        return int(str(v).strip()) if str(v).strip() else None
    except ValueError:
        return None


def _atleta_de_arquivo(a):
    return {'nome': a.get('nome') or a.get('jogador') or '?', 'posicao': mapear_posicao(a.get('posicao')), 'detalhe': a.get('posicao') or '',
            'numero': _inteiro(a.get('numero')), 'nascimento': a.get('nascimento') or None, 'nacionalidade': a.get('nacionalidade') or '',
            'overall': _inteiro(a.get('overall')), 'valor_mercado': _inteiro(a.get('valor_mercado')), 'foto': a.get('foto') or ''}

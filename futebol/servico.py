"""
Camada de serviço: junta os provedores com o banco local e SEMPRE degrada com elegância
(sem chave / sem rede → usa só o que o próprio site já sabe).
"""
import logging
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from accounts.temas import normalizar
from palpites.models import Jogo

from .models import Atleta, Time
from .provedores import api_football, espn, football_data
from .provedores.base import ProvedorIndisponivel

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ busca

def buscar(texto, limite=8):
    """ Busca insensível a acento em times e jogadores. Devolve {'times': [...], 'jogadores': [...]}. """
    q = normalizar(texto)
    if len(q) < 2:
        return {'times': [], 'jogadores': []}
    times = Time.objects.filter(busca__contains=q).order_by('nome')[:limite]
    jogadores = (Atleta.objects.filter(busca__contains=q).select_related('time').order_by('nome')[:limite])
    return {'times': list(times), 'jogadores': list(jogadores)}


# ------------------------------------------------------------------ forma, confronto direto e raio-x

def _letra(pro, contra):
    return 'V' if pro > contra else 'D' if pro < contra else 'E'


def forma_local(nome_time, limite=5):
    """ Últimos resultados do time nos jogos que o próprio Bolão já finalizou. """
    jogos = (Jogo.objects.filter(finalizado=True).filter(Q(time_casa=nome_time) | Q(time_fora=nome_time))
             .exclude(gols_casa_real=None).order_by('-data_hora')[:limite])
    saida = []
    for j in jogos:
        casa = j.time_casa == nome_time
        pro, contra = (j.gols_casa_real, j.gols_fora_real) if casa else (j.gols_fora_real, j.gols_casa_real)
        saida.append({'data': j.data_hora.date().isoformat(), 'casa': j.time_casa, 'fora': j.time_fora,
                      'placar': f"{j.gols_casa_real} x {j.gols_fora_real}", 'resultado': _letra(pro, contra)})
    return list(reversed(saida))


def confronto_local(casa, fora, limite=6):
    jogos = (Jogo.objects.filter(finalizado=True).filter(
        Q(time_casa=casa, time_fora=fora) | Q(time_casa=fora, time_fora=casa))
        .exclude(gols_casa_real=None).order_by('-data_hora')[:limite])
    return [{'data': j.data_hora.date().isoformat(), 'casa': j.time_casa, 'fora': j.time_fora,
             'placar': f"{j.gols_casa_real} x {j.gols_fora_real}", 'gols_casa': j.gols_casa_real, 'gols_fora': j.gols_fora_real}
            for j in jogos]


def resumo_confronto(jogos, casa, fora):
    v_casa = v_fora = empates = 0
    for j in jogos:
        gc, gf = (j['gols_casa'], j['gols_fora'])
        dono_casa, dono_fora = (gc, gf) if j['casa'] == casa else (gf, gc)
        if dono_casa > dono_fora:
            v_casa += 1
        elif dono_casa < dono_fora:
            v_fora += 1
        else:
            empates += 1
    return {'casa': v_casa, 'empates': empates, 'fora': v_fora}


def _time_por_nome(nome):
    chave = normalizar(nome)
    return next((t for t in Time.objects.filter(busca__contains=chave) if normalizar(t.nome) == chave), None)


def raio_x(jogo):
    """
    Panorama do jogo para ajudar no palpite: forma recente, confronto direto, posição na tabela,
    previsão (API-Football) e desfalques. Cada bloco que falhar simplesmente não aparece.
    """
    casa, fora = jogo.time_casa, jogo.time_fora
    fontes = {'banco do site'}
    out = {'casa': casa, 'fora': fora, 'forma_casa': forma_local(casa), 'forma_fora': forma_local(fora),
           'h2h': confronto_local(casa, fora), 'tabela': None, 'previsao': None, 'lesoes_casa': [], 'lesoes_fora': []}

    # forma pelo football-data (se o time tem id e a API respondeu)
    if football_data.disponivel():
        for lado, nome in (('forma_casa', casa), ('forma_fora', fora)):
            tm = _time_por_nome(nome)
            id_ext = (tm.ids_externos.get('football-data') if tm else None)
            if id_ext:
                try:
                    jogos = football_data.ultimos_jogos(id_ext)
                    if jogos:
                        out[lado] = jogos
                        fontes.add('football-data')
                except ProvedorIndisponivel as erro:
                    logger.info("forma indisponível (%s): %s", nome, erro)
        if jogo.external_id:
            try:
                h2h = football_data.confronto_direto(jogo.external_id)
                if h2h:
                    out['h2h'] = h2h
                    fontes.add('football-data')
            except ProvedorIndisponivel as erro:
                logger.info("h2h indisponível: %s", erro)
        try:
            tabela = {l['time']: l for l in football_data_tabela()}
            if casa in tabela and fora in tabela:
                out['tabela'] = {'casa': tabela[casa], 'fora': tabela[fora]}
                fontes.add('football-data')
        except ProvedorIndisponivel:
            pass

    out['resumo_h2h'] = resumo_confronto(out['h2h'], casa, fora) if out['h2h'] else None

    if api_football.disponivel():
        try:
            temporada = jogo.data_hora.year
            out['previsao'] = api_football.previsao_do_jogo(casa, fora, jogo.data_hora.date().isoformat(), temporada)
            lesoes = api_football.lesoes(temporada)
            out['lesoes_casa'], out['lesoes_fora'] = lesoes.get(casa, []), lesoes.get(fora, [])
            fontes.add('api-football')
        except ProvedorIndisponivel as erro:
            logger.info("api-football indisponível: %s", erro)

    out['fontes'] = sorted(fontes)
    return out


def football_data_tabela():
    from palpites import api_futebol
    try:
        return api_futebol.classificacao()
    except api_futebol.ApiIndisponivel as erro:
        raise ProvedorIndisponivel(str(erro))


# ------------------------------------------------------------------ notícias, ao vivo, artilharia

def noticias_gerais(limite=8):
    try:
        return espn.noticias(limite=limite)
    except ProvedorIndisponivel:
        return []


def ao_vivo():
    """ Placar do dia (ESPN). Vazio se indisponível. """
    try:
        return espn.placar()
    except ProvedorIndisponivel:
        return []


def artilharia(limite=10):
    """ Artilharia do Brasileirão: football-data → API-Football → vazio. """
    if football_data.disponivel():
        try:
            return football_data.artilheiros(limite=limite)
        except ProvedorIndisponivel:
            pass
    if api_football.disponivel():
        try:
            return api_football.artilheiros(timezone.localdate().year, limite=limite)
        except ProvedorIndisponivel:
            pass
    return []


# ------------------------------------------------------------------ comparação de times

def comparar_times(a, b):
    """ Números lado a lado calculados do nosso banco de atletas (só o que existe de fato). """
    def stats(t):
        atletas = list(t.atletas.all())
        por_pos = {p: sum(1 for x in atletas if x.posicao == p) for p in ('GOL', 'DEF', 'MEI', 'ATA')}
        overalls = [x.overall for x in atletas if x.overall]
        idades = [x.idade for x in atletas if x.idade]
        valor = sum(x.valor_mercado or 0 for x in atletas)
        top = sorted([x for x in atletas if x.overall], key=lambda x: -x.overall)[:3]
        return {
            'elenco': len(atletas), 'por_pos': por_pos,
            'overall_medio': round(sum(overalls) / len(overalls), 1) if overalls else None,
            'idade_media': round(sum(idades) / len(idades), 1) if idades else None,
            'valor_mercado': valor or None, 'destaques': top,
        }
    sa, sb = stats(a), stats(b)
    linhas = []
    for rotulo, chave, maior_melhor in (('Elenco', 'elenco', True), ('Overall médio', 'overall_medio', True),
                                        ('Idade média', 'idade_media', None), ('Valor de mercado (€)', 'valor_mercado', True)):
        va, vb = sa[chave], sb[chave]
        if va is None and vb is None:
            continue
        vencedor = None
        if maior_melhor and va is not None and vb is not None and va != vb:
            vencedor = 'A' if va > vb else 'B'
        linhas.append({'rotulo': rotulo, 'a': va, 'b': vb, 'vencedor': vencedor})
    return {'a': sa, 'b': sb, 'linhas': linhas}

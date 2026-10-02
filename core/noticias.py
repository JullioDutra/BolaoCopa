"""
Notícias do time do coração para o feed inicial.

Fonte padrão: RSS de busca do Google Notícias restrito ao ge.globo.com (o ge não
oferece widget/embed oficial; o RSS traz só título + link, e o clique abre a
matéria no próprio ge). A URL é configurável em settings.NOTICIAS_RSS_URL, então
dá para trocar por qualquer outro RSS (use {q} onde entra a busca).

Tudo é cacheado e tolerante a falhas: se a rede estiver bloqueada (ex.: lista de
sites liberados do PythonAnywhere gratuito) o feed simplesmente fica vazio.
"""
import logging
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from django.conf import settings
from django.core.cache import cache

from accounts.temas import normalizar

logger = logging.getLogger(__name__)

TTL_NOTICIAS = 30 * 60
TTL_FALHA = 5 * 60
LIMITE_BYTES = 1024 * 1024  # não lê respostas gigantes


def _baixar(url, timeout=5):
    req = urllib.request.Request(url, headers={'User-Agent': 'Cartolandia/1.0 (+feed de noticias)'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(LIMITE_BYTES)


def interpretar_rss(xml_bytes, limite=6):
    """ Converte o XML do RSS em lista de dicts {titulo, link, fonte, publicado_em}. """
    raiz = ET.fromstring(xml_bytes)
    itens = []
    for item in raiz.iter('item'):
        titulo = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        if not titulo or not link.lower().startswith(('http://', 'https://')):
            continue  # descarta links com esquemas estranhos (javascript:, data:...)

        fonte_el = item.find('source')
        fonte = (fonte_el.text or '').strip() if fonte_el is not None and fonte_el.text else ''
        # Google Notícias acrescenta " - Fonte" ao título
        if fonte and titulo.endswith(f' - {fonte}'):
            titulo = titulo[: -len(fonte) - 3].rstrip()

        publicado = None
        bruto = item.findtext('pubDate')
        if bruto:
            try:
                publicado = parsedate_to_datetime(bruto).isoformat()
            except (TypeError, ValueError):
                publicado = None

        itens.append({'titulo': titulo, 'link': link, 'fonte': fonte or 'ge', 'publicado_em': publicado})
        if len(itens) >= limite:
            break
    return itens


def _url(consulta):
    return settings.NOTICIAS_RSS_URL.format(q=urllib.parse.quote_plus(consulta))


def buscar_noticias(clube_nome, limite=6):
    """ Notícias recentes do clube (lista de dicts; vazia se indisponível). """
    chave = f"noticias:{normalizar(clube_nome)}"
    pronto = cache.get(chave)
    if pronto is not None:
        return pronto

    consultas = [f'"{clube_nome}" futebol site:ge.globo.com when:7d', f'"{clube_nome}" futebol when:7d']
    for consulta in consultas:
        try:
            itens = interpretar_rss(_baixar(_url(consulta)), limite=limite)
        except (urllib.error.URLError, TimeoutError, OSError, ET.ParseError, ValueError) as erro:
            logger.warning("Notícias indisponíveis para %s: %s", clube_nome, erro)
            antigas = cache.get(chave + ':antiga')
            cache.set(chave, antigas or [], TTL_FALHA)
            return antigas or []
        if itens:
            cache.set(chave, itens, TTL_NOTICIAS)
            cache.set(chave + ':antiga', itens, 60 * 60 * 24 * 3)
            return itens

    cache.set(chave, [], TTL_FALHA)
    return []

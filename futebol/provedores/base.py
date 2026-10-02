"""HTTP comum aos provedores: timeout curto, cache e um único tipo de erro."""
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.core.cache import cache

logger = logging.getLogger(__name__)


class ProvedorIndisponivel(Exception):
    """ Sem chave, rede bloqueada, limite estourado ou resposta inválida. """


def http_get_json(url, params=None, headers=None, timeout=8, cache_segundos=0):
    """ GET → JSON. Com `cache_segundos`, respostas boas ficam no cache (economiza cota das APIs). """
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    chave = f"http:{url}" if cache_segundos else None
    if chave:
        pronto = cache.get(chave)
        if pronto is not None:
            return pronto
    req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Cartolandia/1.0', **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            dados = json.loads(resp.read(5 * 1024 * 1024).decode('utf-8'))
    except urllib.error.HTTPError as erro:
        raise ProvedorIndisponivel(f"HTTP {erro.code} em {url.split('?')[0]}") from erro
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as erro:
        raise ProvedorIndisponivel(f"Falha ao acessar {url.split('?')[0]}: {erro}") from erro
    if chave:
        cache.set(chave, dados, cache_segundos)
    return dados

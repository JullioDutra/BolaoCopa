"""Resolução global de escudos: nome do clube -> URL do escudo (uma consulta por processo/minuto)."""
import re

from django.core.cache import cache

from accounts.temas import normalizar

CACHE_KEY = 'escudos_global_v1'
RUIDO = {'fc', 'ec', 'sc', 'cf', 'afc', 'cr', 'ac', 'ad', 'fk', 'clube', 'club', 'futebol', 'de', 'do', 'da', 'esporte',
         'regatas', 'e', 'sad', 'sociedade', 'associacao', 'atletica'}


def chave_time(nome):
    """ 'C.R. Flamengo' / 'Flamengo FC' -> 'flamengo'. Mantém o sufixo de estado (atletico mg != atletico go). """
    texto = re.sub(r'[^a-z0-9 ]+', ' ', normalizar(nome).replace('-', ' ').replace('.', ''))
    partes = [p for p in texto.split() if p not in RUIDO]
    return ' '.join(partes) or texto.strip()


def _mapa():
    mapa = cache.get(CACHE_KEY)
    if mapa is None:
        from .models import Escudo
        mapa = {}
        for e in Escudo.objects.all():
            src = e.src
            if not src:
                continue
            mapa[e.chave] = src
            for ap in filter(None, (a.strip() for a in e.apelidos.split(','))):
                mapa.setdefault(chave_time(ap), src)
        cache.set(CACHE_KEY, mapa, 300)
    return mapa


def limpar_cache():
    cache.delete(CACHE_KEY)


def escudo_url(nome):
    """ URL do escudo global do clube ou None. Tolerante a tabela inexistente (antes do migrate). """
    if not nome:
        return None
    try:
        return _mapa().get(chave_time(nome))
    except Exception:
        return None


def registrar(nome, arquivo=None, url=''):
    """ Cria/atualiza o escudo global sem sobrescrever um arquivo já existente. """
    from .models import Escudo
    chave = chave_time(nome)
    if not chave:
        return None
    escudo, criado = Escudo.objects.get_or_create(chave=chave, defaults={'nome': nome})
    mudou = False
    if arquivo and not escudo.arquivo:
        escudo.arquivo = arquivo
        mudou = True
    if url and not escudo.url:
        escudo.url = url
        mudou = True
    if mudou:
        escudo.save()
    return escudo

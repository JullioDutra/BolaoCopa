"""Registro do feed "Resenha ao vivo". Nunca pode quebrar o fluxo principal."""
import logging
import re

from .models import Atividade

logger = logging.getLogger(__name__)


def nome_publico(usuario):
    return (usuario.first_name or usuario.username.split('@')[0]).strip()


def registrar(usuario, tipo, texto, url=''):
    try:
        # o ícone do feed já identifica o tipo: remove emoji/símbolos do começo do texto
        limpo = re.sub(r'^[^\w¡¿"“]+', '', texto).strip() or texto
        return Atividade.objects.create(usuario=usuario, tipo=tipo, texto=limpo[:200], url=url)
    except Exception as erro:             # feed é "bônus": falha aqui não derruba palpite/aposta
        logger.warning("Não foi possível registrar atividade: %s", erro)
        return None


ICONES = {'cravada': ('fa-bullseye', '#dc2626'), 'aposta': ('fa-ticket', '#d97706'), 'conquista': ('fa-medal', '#7c3aed'),
          'voto': ('fa-square-poll-vertical', '#2563eb'), 'streak': ('fa-fire', '#ea580c'), 'rodada': ('fa-trophy', '#ca8a04'),
          'geral': ('fa-futbol', '#16a34a')}


def icone(tipo):
    return ICONES.get(tipo, ICONES['geral'])

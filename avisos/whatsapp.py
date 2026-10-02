"""Atalhos de WhatsApp: links wa.me (sem API, sem custo) e textos prontos para o grupo."""
from urllib.parse import quote

from django.conf import settings


def link_compartilhar(texto):
    """ Abre o WhatsApp para escolher o contato/grupo com o texto preenchido. """
    return f"https://wa.me/?text={quote(texto)}"


def link_chat(telefone, texto=''):
    """ Abre conversa direta com um número (só dígitos com DDI). """
    digitos = ''.join(c for c in (telefone or '') if c.isdigit())
    return f"https://wa.me/{digitos}" + (f"?text={quote(texto)}" if texto else '')


def link_grupo():
    return getattr(settings, 'WHATSAPP_GRUPO_URL', '') or ''


def texto_resumo(ranking, proximos, site_url=''):
    """ Texto pronto para colar no grupo: top do ranking + próximos jogos. """
    linhas = ["🏆 *CARTOLÂNDIA — resumo*", ""]
    if ranking:
        linhas.append("*Ranking geral*")
        medalhas = ['🥇', '🥈', '🥉']
        for i, r in enumerate(ranking[:5]):
            nome = r['usuario'].first_name or r['usuario'].username
            linhas.append(f"{medalhas[i] if i < 3 else f'{i + 1}º'} {nome} — {r['total_pontos']} pts")
        linhas.append("")
    if proximos:
        linhas.append("*Próximos jogos (bora palpitar!)*")
        for j in proximos[:5]:
            linhas.append(f"⚽ {j.time_casa} x {j.time_fora} — {j.data_hora.astimezone().strftime('%d/%m %H:%M')}")
        linhas.append("")
    if site_url:
        linhas.append(f"👉 {site_url}")
    return "\n".join(linhas)

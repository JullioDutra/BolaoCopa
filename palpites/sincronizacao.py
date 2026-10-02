"""
Sincroniza jogos e resultados da API com o Bolão.

  * Cria/atualiza `Jogo` pelo `external_id` (nunca duplica).
  * Agrupa os jogos em `RodadaBolao` (formato "Bolão da Rodada").
  * Quando a API diz FINISHED, grava o placar e marca `finalizado` — o que já
    dispara a pontuação, os prêmios e os Cartola Coins pelo `Jogo.save()`.
  * Nunca mexe em jogo que a staff finalizou manualmente com outro placar,
    e nunca "desfinaliza" um jogo.
"""
from datetime import datetime, timezone as dt_timezone

from django.db import transaction

from futebol import escudos as catalogo_escudos
from . import api_futebol
from .models import Clube, Jogo, RodadaBolao


def _parse_data(iso):
    return datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(dt_timezone.utc)


def _rodada_bolao(campeonato_nome, numero):
    if not numero:
        return None
    rodada, _ = RodadaBolao.objects.get_or_create(
        campeonato=campeonato_nome, numero=numero,
        defaults={'nome': f"{campeonato_nome} — Rodada {numero}"},
    )
    return rodada


def sincronizar(competicao=api_futebol.COMPETICAO_PADRAO, rodada=None, finalizar=True):
    """
    Busca as partidas na API e atualiza o banco. Devolve um resumo:
    {'criados': n, 'atualizados': n, 'finalizados': n, 'total': n}
    Levanta `ApiIndisponivel` se a API não puder ser consultada.
    """
    campeonato_nome = api_futebol.NOMES_COMPETICAO.get(competicao, competicao)
    if rodada is None:
        rodada = api_futebol.rodada_atual(competicao)
    partidas = api_futebol.partidas(competicao, rodada=rodada)

    escudos = {c.nome: c for c in Clube.objects.exclude(escudo='').exclude(escudo__isnull=True)}
    resumo = {'criados': 0, 'atualizados': 0, 'finalizados': 0, 'total': len(partidas)}

    for p in partidas:
        grupo = _rodada_bolao(campeonato_nome, p['rodada'])
        campos = {
            'time_casa': p['casa'],
            'time_fora': p['fora'],
            'data_hora': _parse_data(p['data_hora']),
            'campeonato': campeonato_nome,
            'status_externo': p['status'],
            'escudo_casa_url': p['escudo_casa'],
            'escudo_fora_url': p['escudo_fora'],
            'rodada': grupo,
        }

        # Catálogo global: o escudo da API entra uma vez e vale para todos os jogos do site
        for nome_time, url_time in ((p['casa'], p['escudo_casa']), (p['fora'], p['escudo_fora'])):
            if nome_time and url_time:
                catalogo_escudos.registrar(nome_time, url=url_time)

        with transaction.atomic():
            jogo = Jogo.objects.select_for_update().filter(external_id=p['external_id']).first()
            criado = jogo is None
            if criado:
                jogo = Jogo(external_id=p['external_id'])
                # Escudos já enviados no Admin têm prioridade sobre os da API
                if p['casa'] in escudos:
                    jogo.escudo_casa = escudos[p['casa']].escudo
                if p['fora'] in escudos:
                    jogo.escudo_fora = escudos[p['fora']].escudo

            if not jogo.finalizado:
                for campo, valor in campos.items():
                    setattr(jogo, campo, valor)

            terminou = (
                finalizar and p['status'] == 'FINISHED'
                and p['gols_casa'] is not None and p['gols_fora'] is not None
                and not jogo.finalizado
            )
            if terminou:
                jogo.gols_casa_real = p['gols_casa']
                jogo.gols_fora_real = p['gols_fora']
                jogo.finalizado = True
            elif p['status'] in ('IN_PLAY', 'PAUSED') and not jogo.finalizado:
                # Placar parcial só para exibir ao vivo; não finaliza
                jogo.gols_casa_real = p['gols_casa']
                jogo.gols_fora_real = p['gols_fora']

            jogo.save()

        if criado:
            resumo['criados'] += 1
        else:
            resumo['atualizados'] += 1
        if terminou:
            resumo['finalizados'] += 1
    return resumo

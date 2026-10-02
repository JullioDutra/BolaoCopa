"""Draft (Copa do Brasil e Busca pelo Mundial): sorteia times históricos, monta o XI e disputa 7 jogos."""
import random
import re
import secrets

from django.db import transaction
from django.utils import timezone

from accounts import coins

from . import dados, engine
from .models import DraftCopa7a0, Partida7a0

FASES = ['1ª fase', '2ª fase', '3ª fase', 'Oitavas de final', 'Quartas de final', 'Semifinal', 'Final']
FASES_MUNDIAL = ['Grupo · Jogo 1', 'Grupo · Jogo 2', 'Grupo · Jogo 3', 'Oitavas de final', 'Quartas de final', 'Semifinal', 'Final']
TORNEIOS = {
    'brasil': {'nome': 'Copa do Brasil', 'fases': FASES, 'campeao': 500, 'invicto': 300, 'vitoria': 15},
    'mundial': {'nome': 'Busca pelo Mundial', 'fases': FASES_MUNDIAL, 'campeao': 2500, 'invicto': 2000, 'vitoria': 40, 'skips': 5},
}
JOGOS_DE_GRUPO = 3
BANCO = 5
SKIPS = 3
PREMIO_CAMPEAO = 500
PREMIO_INVICTO = 300
PREMIO_POR_VITORIA = 15
LIMITE_PREMIADOS_POR_DIA = 3
CUSTO_MAXIMO_ADAPTACAO = 8


class ErroDraft(Exception):
    pass


# ------------------------------------------------------------------ montagem

def fases_de(draft):
    return TORNEIOS[draft.torneio]['fases']


def grupo_ativo(draft):
    """ True enquanto o draft do Mundial ainda está na fase de grupos. """
    return draft.torneio == 'mundial' and draft.fase < JOGOS_DE_GRUPO


def mundial_liberado(usuario):
    """ A Busca pelo Mundial só abre para quem já foi campeão da Copa do Brasil. """
    return DraftCopa7a0.objects.filter(usuario=usuario, torneio='brasil', status='campeao').exists()


def criar_draft(usuario, formacao='4-3-3', mentalidade='equilibrado', torneio='brasil'):
    """ Sempre mata-mata: perdeu uma fase, está eliminado. """
    if formacao not in dados.FORMACOES:
        formacao = '4-3-3'
    if mentalidade not in engine.MENTALIDADES:
        mentalidade = 'equilibrado'
    if torneio not in TORNEIOS:
        torneio = 'brasil'
    if torneio == 'mundial' and not mundial_liberado(usuario):
        raise ErroDraft('A Busca pelo Mundial só abre para quem foi campeão da Copa do Brasil.')
    estado = {'slots': [None] * 11, 'banco': [None] * BANCO, 'sorteadas': [], 'pendente': None, 'skips': TORNEIOS[torneio].get('skips', SKIPS), 'rivais': []}
    return DraftCopa7a0.objects.create(usuario=usuario, torneio=torneio, formacao=formacao, mentalidade=mentalidade,
                                       eliminatorio=True, estado=estado)


def _escolhas(draft):
    return [j for j in draft.estado['slots'] + draft.estado['banco'] if j]


def vagas(draft):
    e = draft.estado
    return {'slots': [i for i, j in enumerate(e['slots']) if j is None], 'banco': [i for i, j in enumerate(e['banco']) if j is None]}


def completo(draft):
    v = vagas(draft)
    return not v['slots'] and not v['banco']


def posicoes_slots(draft):
    return dados.FORMACOES[draft.formacao]


def _sortear_time(draft, excluir=None):
    e = draft.estado
    pool = [k for k in dados.TIMES if k not in e['sorteadas'] and k != excluir]
    if not pool:
        e['sorteadas'] = []
        pool = [k for k in dados.TIMES if k != excluir]
    return secrets.choice(pool)


def sortear(draft):
    """ Rola o dado: devolve a chave do time sorteado (a mesma, se já houver um pendente). """
    if draft.status != 'montando':
        raise ErroDraft('O draft já terminou.')
    if completo(draft):
        raise ErroDraft('Time completo! Comece a Copa.')
    e = draft.estado
    if not e['pendente']:
        e['pendente'] = _sortear_time(draft)
        e['sorteadas'].append(e['pendente'])
        draft.save(update_fields=['estado'])
    return e['pendente']


def pular(draft):
    """ Usa um dos "re-sorteios": troca o time pendente por outro. """
    if draft.status != 'montando' or not draft.estado['pendente']:
        raise ErroDraft('Nada para pular agora.')
    e = draft.estado
    if e['skips'] <= 0:
        raise ErroDraft('Acabaram os re-sorteios.')
    e['skips'] -= 1
    e['pendente'] = _sortear_time(draft, excluir=e['pendente'])
    e['sorteadas'].append(e['pendente'])
    draft.save(update_fields=['estado'])
    return e['pendente']


def _nome_unico(draft, nome, time):
    usados = {j['nome'] for j in _escolhas(draft)}
    if nome not in usados:
        return nome
    return f"{nome} ({time['clube'][:3].upper()}{time['ano'] % 100:02d})"


def escolher(draft, nome, destino):
    """ Coloca um jogador do time pendente no slot `destino` (índice 0–10) ou no 'banco'. """
    if draft.status != 'montando':
        raise ErroDraft('O draft já terminou.')
    e = draft.estado
    if not e['pendente']:
        raise ErroDraft('Role o dado primeiro.')
    time = dados.obter(e['pendente'])
    original = next((j for j in time['elenco'] if j['nome'] == nome), None)
    if not original:
        raise ErroDraft('Esse jogador não está no time sorteado.')
    jogador = dict(original)
    jogador['nome'] = _nome_unico(draft, nome, time)
    jogador['origem'] = time['nome']
    jogador['adaptado'] = False
    if destino == 'banco':
        livres = vagas(draft)['banco']
        if not livres:
            raise ErroDraft('O banco já está cheio.')
        e['banco'][livres[0]] = jogador
    else:
        try:
            i = int(destino)
            alvo = posicoes_slots(draft)[i]
        except (TypeError, ValueError, IndexError):
            raise ErroDraft('Posição inválida.')
        if e['slots'][i] is not None:
            raise ErroDraft('Essa posição já foi preenchida.')
        custo = dados.custo_posicao(original['pos'], alvo)
        if custo > CUSTO_MAXIMO_ADAPTACAO:
            raise ErroDraft(f"{original['nome']} ({original['pos']}) não joga de {alvo}.")
        if custo:
            jogador = {**dados._jogador(jogador['nome'], alvo, max(40, original['nota'] - custo)),
                       'origem': time['nome'], 'adaptado': True, 'natural': original['pos']}
        e['slots'][i] = jogador
    e['pendente'] = None
    draft.save(update_fields=['estado'])
    return jogador


# ------------------------------------------------------------------ copa

def time_do_draft(draft):
    e = draft.estado
    nome = f"Time do {draft.usuario.first_name or draft.usuario.username}"[:30]
    elenco = [j for j in e['slots'] if j] + [j for j in e['banco'] if j]
    return {'chave': f'draft-{draft.pk}', 'clube': 'Seu Time', 'ano': timezone.now().year, 'nome': nome, 'apelido': 'Seleção dos sonhos',
            'cor': '#0f766e', 'formacao': draft.formacao, 'tecnico': draft.usuario.first_name or draft.usuario.username,
            'elenco': elenco, 'forca': dados.forcas([j for j in e['slots'] if j])}


def _sortear_rivais():
    """ Só times históricos "de verdade", dos mais fracos (1ª fase) aos mais fortes (final). """
    historicos = [t['chave'] for t in dados.todos()][::-1]   # do mais fraco ao mais forte
    n = len(historicos)
    faixas = [(0, n // 5), (0, n // 4), (n // 8, n // 3), (n // 4, int(n * 0.5)),
              (int(n * 0.4), int(n * 0.65)), (int(n * 0.6), int(n * 0.85)), (n - 6, n)]
    rivais = []
    for a, b in faixas:
        cand = [k for k in historicos[a:b] if k not in rivais] or [k for k in historicos if k not in rivais]
        rivais.append(secrets.choice(cand))
    return rivais


def _sortear_mundial(chave_usuario):
    """ Sorteio de grupo estilo Mundial (potes) + 4 adversários de mata-mata do mais fraco ao mais forte. """
    mundo = [t['chave'] for t in dados.mundo()]               # do mais forte ao mais fraco
    n = len(mundo)
    potes = [mundo[:n // 3], mundo[n // 3: 2 * n // 3], mundo[2 * n // 3:]]
    grupo = [secrets.choice(p) for p in potes]
    restantes = [k for k in reversed(mundo) if k not in grupo]  # do mais fraco ao mais forte
    m = len(restantes)
    faixas = [(0, m // 2), (m // 4, 3 * m // 4), (m // 2, m), (m - 3, m)]
    mata = []
    for a, b in faixas:
        cand = [k for k in restantes[a:b] if k not in mata] or [k for k in restantes if k not in mata]
        mata.append(secrets.choice(cand))
    mata.sort(key=lambda k: dados.obter(k)['overall'])   # o mata-mata sempre sobe de nível
    return grupo + mata


def _tabela_vazia():
    return {'pj': 0, 'v': 0, 'e': 0, 'd': 0, 'gp': 0, 'gc': 0, 'pts': 0}


def iniciar_copa(draft):
    if draft.status != 'montando':
        raise ErroDraft('A Copa já começou.')
    if not completo(draft):
        raise ErroDraft('Complete os 11 titulares e os 5 reservas.')
    if draft.torneio == 'mundial':
        draft.estado['rivais'] = _sortear_mundial(f'draft-{draft.pk}')
        u = f'draft-{draft.pk}'
        a, b, c = draft.estado['rivais'][:3]
        draft.estado['grupo'] = {
            'times': [u, a, b, c],
            'rodadas': [[[u, a], [b, c]], [[u, b], [a, c]], [[u, c], [a, b]]],
            'tabela': {k: _tabela_vazia() for k in (u, a, b, c)}, 'resultados': [],
        }
    else:
        draft.estado['rivais'] = _sortear_rivais()
    draft.status = 'copa'
    draft.save(update_fields=['estado', 'status'])


def partida_da_fase(draft):
    """ Partida (criada sob demanda) da fase atual; None se a copa acabou. """
    from .servico import criar_partida_draft
    if draft.status != 'copa':
        return None
    existente = draft.partidas.filter(fase=draft.fase).first()
    return existente or criar_partida_draft(draft)


def _sufixo(nome):
    return re.sub(r'\s*\([A-Z]{3}\d{2}\)$', '', nome)


def _registrar_jogo(tab, casa, fora, gc, gf):
    for chave, gp, gs in ((casa, gc, gf), (fora, gf, gc)):
        t = tab[chave]
        t['pj'] += 1
        t['gp'] += gp
        t['gc'] += gs
        if gp > gs:
            t['v'] += 1
            t['pts'] += 3
        elif gp == gs:
            t['e'] += 1
            t['pts'] += 1
        else:
            t['d'] += 1


def classificacao_grupo(draft):
    """ Tabela do grupo ordenada (pontos, vitórias, saldo, gols pró) com a chave do usuário marcada. """
    g = draft.estado.get('grupo')
    if not g:
        return []
    u = f'draft-{draft.pk}'
    linhas = [dict(chave=k, **v, sg=v['gp'] - v['gc'], eu=k == u) for k, v in g['tabela'].items()]
    linhas.sort(key=lambda l: (-l['pts'], -l['v'], -l['sg'], -l['gp'], not l['eu']))
    for i, l in enumerate(linhas, 1):
        l['pos'] = i
        l['nome'] = time_do_draft(draft)['nome'] if l['eu'] else dados.obter(l['chave'])['nome']
    return linhas


@transaction.atomic
def registrar_resultado(draft_id, partida):
    """ Chamado quando a partida do draft termina: avança a fase, elimina ou coroa. """
    draft = DraftCopa7a0.objects.select_for_update().get(pk=draft_id)
    if draft.status != 'copa' or partida.fase != draft.fase:
        return draft
    e = partida.estado
    lado = partida.lado_usuario
    rival = dados.obter(partida.time_rival)
    fases = fases_de(draft)
    em_grupo = grupo_ativo(draft)
    venceu = engine.vencedor(e) == lado if not em_grupo else partida.gols_usuario > partida.gols_rival
    pen = e.get('penaltis')
    resultado = 'V' if venceu else ('E' if em_grupo and partida.gols_usuario == partida.gols_rival else 'D')
    draft.campanha = draft.campanha + [{
        'fase': draft.fase, 'nome_fase': fases[draft.fase], 'rival': partida.time_rival, 'rival_nome': rival['nome'],
        'gols_pro': partida.gols_usuario, 'gols_contra': partida.gols_rival,
        'penaltis': f"{pen[lado]}-{pen['fora' if lado == 'casa' else 'casa']}" if pen else '',
        'resultado': resultado, 'partida': partida.pk,
    }]
    if em_grupo:
        _fechar_rodada_do_grupo(draft, partida)
    draft.fase += 1
    if em_grupo:
        if draft.fase >= JOGOS_DE_GRUPO:
            pos = next(l['pos'] for l in classificacao_grupo(draft) if l['eu'])
            draft.estado['grupo_pos'] = pos
            if pos > 2:
                draft.status = 'eliminado'
    elif not venceu:
        draft.status = 'eliminado'
    elif draft.fase >= len(fases):
        draft.status = 'campeao'
    if draft.status != 'copa':
        _fechar(draft)
    draft.save()
    return draft


def _fechar_rodada_do_grupo(draft, partida):
    """ Anota o jogo do usuário e simula o outro jogo da rodada. """
    g = draft.estado['grupo']
    u = f'draft-{draft.pk}'
    r = draft.fase
    for casa, fora in g['rodadas'][r]:
        if u in (casa, fora):
            gc, gf = (partida.gols_usuario, partida.gols_rival) if casa == u else (partida.gols_rival, partida.gols_usuario)
        else:
            seed = (partida.estado['seed'] * 7 + r * 31 + sum(map(ord, casa + fora))) & 0x7fffffff
            final = engine.simular_rapido(casa, fora, seed)
            gc, gf = final['placar']['casa'], final['placar']['fora']
        _registrar_jogo(g['tabela'], casa, fora, gc, gf)
        g['resultados'].append({'rodada': r + 1, 'casa': casa, 'fora': fora, 'gc': gc, 'gf': gf})


def _fechar(draft):
    draft.finalizado_em = timezone.now()
    cfg = TORNEIOS[draft.torneio]
    vitorias = sum(1 for c in draft.campanha if c['resultado'] == 'V')
    derrotas = sum(1 for c in draft.campanha if c['resultado'] == 'D')
    penaltis = sum(1 for c in draft.campanha if c['penaltis'])
    draft.invicto = draft.status == 'campeao' and derrotas == 0 and penaltis == 0
    premio = vitorias * cfg['vitoria']
    if draft.status == 'campeao':
        premio += cfg['campeao'] + (cfg['invicto'] if draft.invicto else 0)
    hoje = timezone.localdate()
    premiados = DraftCopa7a0.objects.filter(usuario=draft.usuario, premio__gt=0, finalizado_em__date=hoje).count()
    if premio and premiados < LIMITE_PREMIADOS_POR_DIA:
        draft.premio = premio
        coins.creditar(draft.usuario, premio, f"🏆 7 a 0 {cfg['nome']}: {titulo(draft)['curto']}")
    draft.save()   # as conquistas leem o banco: o título precisa estar salvo antes
    try:
        from avisos import atividade, conquistas
        nome = atividade.nome_publico(draft.usuario)
        if draft.status == 'campeao':
            atividade.registrar(draft.usuario, 'rodada', f"{nome} foi campeão da {cfg['nome']} do 7 a 0 ({titulo(draft)['curto'].lower()})",
                                url=f'/setezero/r/{draft.codigo}/')
        conquistas.checar(draft.usuario)
    except Exception:
        pass


# ------------------------------------------------------------------ retrospecto

def titulo(draft):
    """ Manchete do retrospecto. """
    camp = draft.campanha
    cfg = TORNEIOS[draft.torneio]
    mundial = draft.torneio == 'mundial'
    v = sum(1 for c in camp if c['resultado'] == 'V')
    d = sum(1 for c in camp if c['resultado'] == 'D')
    pen = sum(1 for c in camp if c['penaltis'])
    if draft.status == 'campeao' and draft.invicto:
        return {'curto': 'Campeão invicto', 'manchete': '7 A 0! CAMPEÃO DO MUNDO INVICTO' if mundial else '7 A 0! CAMPEÃO INVICTO', 'classe': 'ouro',
                'sub': 'O Brasil calou a Europa: sete vitórias no tempo normal.' if mundial else 'Sete vitórias no tempo normal. Ninguém te parou.'}
    if draft.status == 'campeao' and d == 0:
        return {'curto': 'Campeão sem perder', 'manchete': 'CAMPEÃO DO MUNDO SEM PERDER' if mundial else 'CAMPEÃO SEM PERDER', 'classe': 'ouro',
                'sub': f'Precisou de {pen} disputa{"s" if pen != 1 else ""} de pênaltis, mas nunca caiu.' if pen else 'Sem derrotas no caminho.'}
    if draft.status == 'campeao':
        return {'curto': 'Campeão', 'manchete': 'CAMPEÃO DO MUNDO' if mundial else 'CAMPEÃO DA COPA', 'classe': 'prata',
                'sub': f'Levou o título com {d} derrota{"s" if d != 1 else ""} no caminho.'}
    if draft.status == 'eliminado':
        if mundial and draft.estado.get('grupo_pos', 0) > 2:
            return {'curto': 'Eliminado na fase de grupos', 'manchete': 'ELIMINADO · FASE DE GRUPOS', 'classe': 'bronze',
                    'sub': f'Terminou em {draft.estado["grupo_pos"]}º no grupo.'}
        fase = camp[-1]['nome_fase'] if camp else cfg['fases'][0]
        return {'curto': f'Eliminado: {fase}', 'manchete': f'ELIMINADO · {fase.upper()}', 'classe': 'bronze',
                'sub': f'Caiu para o {camp[-1]["rival_nome"]}.' if camp else ''}
    return {'curto': 'Em andamento', 'manchete': f'{cfg["nome"].upper()} EM ANDAMENTO', 'classe': 'bronze', 'sub': ''}


def retrospecto(draft):
    """ Tudo o que a página compartilhável precisa. """
    from futebol.escudos import escudo_url
    camp = []
    for c in draft.campanha:
        rival = dados.obter(c['rival'])
        camp.append({**c, 'rival_ano': rival['ano'], 'rival_cor': rival['cor'], 'escudo': escudo_url(rival['clube']) or '',
                     'rival_clube': rival['clube']})
    gols = {}
    notas = {}
    for p in draft.partidas.filter(resultado__in=['V', 'E', 'D']):
        for ev in p.estado['eventos']:
            if ev['tipo'] == 'gol' and ev['lado'] == p.lado_usuario and ev['jogador']:
                gols[_sufixo(ev['jogador'])] = gols.get(_sufixo(ev['jogador']), 0) + 1
        for nome, nota in p.estado['notas'].items():
            if nome in {j['nome'] for j in _escolhas(draft)}:
                notas.setdefault(_sufixo(nome), []).append(nota)
    artilheiros = sorted(gols.items(), key=lambda kv: -kv[1])[:5]
    craque = max(notas.items(), key=lambda kv: sum(kv[1]) / len(kv[1]) if len(kv[1]) >= 2 else sum(kv[1]) / len(kv[1]) - 0.5)[0] if notas else None
    e = draft.estado
    linhas = {'GOL': [], 'DEF': [], 'MEI': [], 'ATA': []}
    for j in e['slots']:
        if j:
            g = 'GOL' if j['pos'] == 'GOL' else 'DEF' if j['pos'] in ('ZAG', 'LAT') else 'ATA' if j['pos'] in ('ATA', 'PON') else 'MEI'
            linhas[g].append({**j, 'nome': _sufixo(j['nome'])})
    return {'draft': draft, 'titulo': titulo(draft), 'camp': camp,
            'fases': [{'nome': nome, 'feito': camp[i] if i < len(camp) else None} for i, nome in enumerate(fases_de(draft))],
            'cfg': TORNEIOS[draft.torneio], 'empates': sum(1 for c in camp if c['resultado'] == 'E'),
            'grupo': classificacao_grupo(draft),
            'vitorias': sum(1 for c in camp if c['resultado'] == 'V'), 'derrotas': sum(1 for c in camp if c['resultado'] == 'D'),
            'penaltis': sum(1 for c in camp if c['penaltis']),
            'gols_pro': sum(c['gols_pro'] for c in camp), 'gols_contra': sum(c['gols_contra'] for c in camp),
            'artilheiros': artilheiros, 'craque': craque,
            'linhas': [linhas['ATA'], linhas['MEI'], linhas['DEF'], linhas['GOL']],
            'banco': [{**j, 'nome': _sufixo(j['nome'])} for j in e['banco'] if j],
            'tecnico': draft.usuario.first_name or draft.usuario.username.split('@')[0]}

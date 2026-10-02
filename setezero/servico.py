"""Regras de negócio do "7 a 0": criar partida/temporada, ajustar, finalizar, premiar, ranking."""
import random
import secrets
import zlib

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from accounts import coins

from . import dados, engine
from .models import DraftCopa7a0, Partida7a0, Temporada7a0

PREMIO_VITORIA = 20
PREMIO_EMPATE = 8
PREMIO_GOLEADA = 40         # vitória por 4+ gols
PREMIO_SETE_A_ZERO = 300    # vitória por 7+ gols
PREMIOS_TEMPORADA = {1: 400, 2: 200, 3: 100}
LIMITE_PREMIADAS_POR_DIA = 8
TIMES_NA_TEMPORADA = 8


class ErroJogo(Exception):
    pass


# ------------------------------------------------------------------ partida avulsa

def _validar(chave, aceita_fregues=False):
    time = dados.obter(chave)
    if not time or (time.get('freguesa') and not aceita_fregues):
        raise ErroJogo('Time inválido.')
    return time


def criar_partida(usuario, modo, time_usuario, time_rival=None, formacao=None, mentalidade='equilibrado',
                  estilo='posse', titulares=None, temporada=None, rodada=None, lado='casa'):
    if modo not in ('amistoso', 'desafio', 'temporada'):
        raise ErroJogo('Modo inválido.')
    meu = _validar(time_usuario)
    if modo == 'desafio':
        rival = dados.obter(time_rival) if time_rival in dados.FREGUESES else random.choice(dados.fregueses())
    else:
        rival = _validar(time_rival) if time_rival else random.choice([t for t in dados.TIMES.values() if t['chave'] != time_usuario])
    if rival['chave'] == meu['chave']:
        raise ErroJogo('Escolha um adversário diferente.')
    formacao = formacao if formacao in dados.FORMACOES else meu['formacao']
    if mentalidade not in engine.MENTALIDADES:
        mentalidade = 'equilibrado'
    if estilo not in engine.ESTILOS:
        estilo = 'posse'
    seed = secrets.randbelow(2 ** 31)
    cfg_usuario = {'time': meu['chave'], 'formacao': formacao, 'mentalidade': mentalidade, 'estilo': estilo, 'titulares': titulares}
    cfg_rival = {'time': rival['chave'], 'mentalidade': 'equilibrado', 'estilo': random.Random(seed).choice(list(engine.ESTILOS))}
    casa, fora = (cfg_usuario, cfg_rival) if lado == 'casa' else (cfg_rival, cfg_usuario)
    estado = engine.novo_estado(casa, fora, seed, usuario_lado=lado)
    return Partida7a0.objects.create(usuario=usuario, modo=modo, temporada=temporada, rodada=rodada, lado_usuario=lado,
                                     time_usuario=meu['chave'], time_rival=rival['chave'], estado=estado)


def criar_partida_draft(draft):
    """ Partida da fase atual do draft: seu time (custom) contra o rival sorteado para a fase. """
    from . import copa
    time = copa.time_do_draft(draft)
    xi = [j['nome'] for j in draft.estado['slots']]
    rival_chave = draft.estado['rivais'][draft.fase]
    rival = dados.obter(rival_chave)
    seed = secrets.randbelow(2 ** 31)
    cfg_u = {'time': time['chave'], 'time_obj': time, 'formacao': draft.formacao, 'mentalidade': draft.mentalidade,
             'estilo': 'posse', 'titulares': xi}
    cfg_r = {'time': rival_chave, 'mentalidade': 'equilibrado', 'estilo': random.Random(seed).choice(list(engine.ESTILOS))}
    estado = engine.novo_estado(cfg_u, cfg_r, seed, usuario_lado='casa', mata_mata=True)
    return Partida7a0.objects.create(usuario=draft.usuario, modo='copa', draft=draft, fase=draft.fase, lado_usuario='casa',
                                     time_usuario=time['chave'], time_rival=rival_chave, estado=estado)


def _sync(partida):
    e = partida.estado
    rival = 'fora' if partida.lado_usuario == 'casa' else 'casa'
    partida.status = e['status']
    partida.gols_usuario = e['placar'][partida.lado_usuario]
    partida.gols_rival = e['placar'][rival]


def avancar(partida, ate='fim', maximo_minutos=None):
    """ Avança a partida e salva. Devolve os eventos novos. Finaliza (premia) quando acaba. """
    if partida.status == 'fim':
        return []
    if isinstance(ate, str) and ate.isdigit():
        ate = int(ate)
    if ate not in ('intervalo', 'fim') and not isinstance(ate, int):
        ate = 'fim'
    novos = engine.avancar(partida.estado, ate, maximo_minutos)
    _sync(partida)
    partida.save(update_fields=['estado', 'status', 'gols_usuario', 'gols_rival'])
    if partida.status == 'fim':
        finalizar(partida)
    return novos


def ajustar(partida, ajuste):
    if partida.status == 'fim':
        raise ErroJogo('A partida já acabou.')
    ok, msg = engine.aplicar_ajuste(partida.estado, partida.lado_usuario, ajuste)
    if not ok:
        raise ErroJogo(msg)
    partida.save(update_fields=['estado'])


def _premio_de(partida):
    saldo = partida.saldo
    if saldo > 0:
        premio = PREMIO_VITORIA
        if saldo >= 4:
            premio += PREMIO_GOLEADA
        if saldo >= 7:
            premio += PREMIO_SETE_A_ZERO
        return premio
    return PREMIO_EMPATE if saldo == 0 else 0


@transaction.atomic
def finalizar(partida):
    """ Fecha a partida: resultado, prêmio em Cartola Coins (com teto diário), feed, conquistas e temporada. """
    partida = Partida7a0.objects.select_for_update().get(pk=partida.pk)
    if partida.finalizado_em:
        return partida
    saldo = partida.saldo
    partida.resultado = 'V' if saldo > 0 else 'E' if saldo == 0 else 'D'
    if partida.estado.get('mata_mata') and saldo == 0:
        partida.resultado = 'V' if engine.vencedor(partida.estado) == partida.lado_usuario else 'D'
    partida.finalizado_em = timezone.now()
    if partida.modo == 'copa':
        partida.save()
        from . import copa
        copa.registrar_resultado(partida.draft_id, partida)
        return partida
    if partida.modo == 'desafio' and saldo < 7:
        premio = PREMIO_VITORIA if saldo > 0 else 0   # desafio só paga bem a goleada
        premio = premio + (PREMIO_GOLEADA if saldo >= 4 else 0)
    else:
        premio = _premio_de(partida)
    hoje = timezone.localdate()
    premiadas_hoje = Partida7a0.objects.filter(usuario=partida.usuario, premio__gt=0, finalizado_em__date=hoje).count()
    if premio and premiadas_hoje < LIMITE_PREMIADAS_POR_DIA:
        partida.premio = premio
        meu, rival = dados.obter(partida.time_usuario), dados.obter(partida.time_rival)
        coins.creditar(partida.usuario, premio, f"⚽ 7 a 0: {meu['nome']} {partida.gols_usuario} x {partida.gols_rival} {rival['nome']}")
    partida.save()
    _pos_jogo(partida)
    return partida


def _pos_jogo(partida):
    try:
        from avisos import atividade, conquistas
        meu, rival = dados.obter(partida.time_usuario), dados.obter(partida.time_rival)
        nome = atividade.nome_publico(partida.usuario)
        if partida.saldo >= 4:
            atividade.registrar(partida.usuario, 'geral',
                                f"{nome} deu uma goleada no 7 a 0: {meu['nome']} {partida.gols_usuario} x {partida.gols_rival} {rival['nome']}",
                                url='/setezero/')
        conquistas.checar(partida.usuario)
    except Exception:
        pass
    if partida.temporada_id:
        concluir_rodada(partida.temporada, partida)


# ------------------------------------------------------------------ temporada

def _calendario(times):
    """ Pontos corridos ida e volta (método do círculo): lista de rodadas, cada uma com [casa, fora]. """
    lista = list(times)
    n = len(lista)
    rodadas = []
    for r in range(n - 1):
        jogos = []
        for i in range(n // 2):
            a, b = lista[i], lista[n - 1 - i]
            jogos.append([a, b] if (r + i) % 2 == 0 else [b, a])
        rodadas.append(jogos)
        lista = [lista[0]] + [lista[-1]] + lista[1:-1]
    volta = [[[b, a] for a, b in rodada] for rodada in rodadas]
    return rodadas + volta


def _linha_vazia():
    return {'pj': 0, 'v': 0, 'e': 0, 'd': 0, 'gp': 0, 'gc': 0, 'pts': 0}


def criar_temporada(usuario, time_usuario):
    meu = _validar(time_usuario)
    outros = random.sample([k for k in dados.TIMES if k != meu['chave']], TIMES_NA_TEMPORADA - 1)
    times = [meu['chave']] + outros
    random.shuffle(times)
    estado = {'times': times, 'calendario': _calendario(times), 'rodada': 0,
              'tabela': {t: _linha_vazia() for t in times}, 'resultados': [], 'seed': secrets.randbelow(2 ** 31)}
    return Temporada7a0.objects.create(usuario=usuario, time_usuario=meu['chave'], estado=estado)


def tabela_ordenada(temporada):
    tab = temporada.estado['tabela']
    linhas = [dict(chave=k, **v, sg=v['gp'] - v['gc']) for k, v in tab.items()]
    linhas.sort(key=lambda l: (-l['pts'], -l['v'], -l['sg'], -l['gp'], l['chave']))
    for i, l in enumerate(linhas, 1):
        l['pos'] = i
        l['time'] = dados.obter(l['chave'])
    return linhas


def _registrar(estado, casa, fora, gc, gf, rodada):
    tab = estado['tabela']
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
    estado['resultados'].append({'rodada': rodada + 1, 'casa': casa, 'fora': fora, 'gc': gc, 'gf': gf})


def jogo_do_usuario(temporada):
    """ [casa, fora, lado] do jogo do usuário na rodada atual, ou None se a temporada acabou. """
    e = temporada.estado
    if e['rodada'] >= len(e['calendario']):
        return None
    for casa, fora in e['calendario'][e['rodada']]:
        if temporada.time_usuario in (casa, fora):
            return casa, fora, 'casa' if casa == temporada.time_usuario else 'fora'
    return None


def partida_da_rodada(temporada):
    """ Partida (criada sob demanda) do usuário na rodada atual; None se a temporada acabou. """
    jogo = jogo_do_usuario(temporada)
    if not jogo:
        return None
    rodada = temporada.estado['rodada']
    existente = temporada.partidas.filter(rodada=rodada).first()
    if existente:
        return existente
    casa, fora, lado = jogo
    rival = fora if lado == 'casa' else casa
    return criar_partida(temporada.usuario, 'temporada', temporada.time_usuario, rival, temporada=temporada, rodada=rodada, lado=lado)


@transaction.atomic
def concluir_rodada(temporada, partida):
    """ Depois do jogo do usuário: simula os outros jogos da rodada, atualiza a tabela e avança. """
    temporada = Temporada7a0.objects.select_for_update().get(pk=temporada.pk)
    e = temporada.estado
    if partida.rodada != e['rodada'] or temporada.status == 'finalizada':
        return temporada
    for casa, fora in e['calendario'][e['rodada']]:
        if temporada.time_usuario in (casa, fora):
            gc = partida.estado['placar']['casa']
            gf = partida.estado['placar']['fora']
        else:
            seed = (e['seed'] * 31 + e['rodada'] * 997 + zlib.crc32(f'{casa}-{fora}'.encode()) % 1000) & 0x7fffffff
            final = engine.simular_rapido(casa, fora, seed)
            gc, gf = final['placar']['casa'], final['placar']['fora']
        _registrar(e, casa, fora, gc, gf, e['rodada'])
    e['rodada'] += 1
    if e['rodada'] >= len(e['calendario']):
        _fechar_temporada(temporada)
    temporada.estado = e
    temporada.save()
    return temporada


def _fechar_temporada(temporada):
    linhas = tabela_ordenada(temporada)
    pos = next(l['pos'] for l in linhas if l['chave'] == temporada.time_usuario)
    temporada.status = 'finalizada'
    temporada.posicao_final = pos
    premio = PREMIOS_TEMPORADA.get(pos, 0)
    if premio:
        temporada.premio = premio
        meu = dados.obter(temporada.time_usuario)
        coins.creditar(temporada.usuario, premio, f"🏆 7 a 0: {pos}º lugar com {meu['nome']}")
    try:
        from avisos import atividade
        atividade.registrar(temporada.usuario, 'rodada',
                            f"{atividade.nome_publico(temporada.usuario)} terminou em {pos}º no campeonato do 7 a 0 com {dados.obter(temporada.time_usuario)['nome']}",
                            url='/setezero/ranking/')
    except Exception:
        pass


# ------------------------------------------------------------------ ranking e visão

def ranking():
    """ Quadro de honra do jogo. """
    from django.contrib.auth.models import User
    base = Partida7a0.objects.filter(resultado__in=['V', 'E', 'D']).exclude(modo='copa')
    craques = (User.objects.annotate(
        jogos=Count('partidas_7a0', filter=Q(partidas_7a0__resultado__in=['V', 'E', 'D'])),
        vitorias=Count('partidas_7a0', filter=Q(partidas_7a0__resultado='V')),
        titulos=Count('temporadas_7a0', filter=Q(temporadas_7a0__posicao_final=1), distinct=True),
    ).filter(jogos__gt=0).order_by('-titulos', '-vitorias', 'first_name')[:15])
    goleadas = []
    for p in base.select_related('usuario'):
        if p.saldo >= 3:
            goleadas.append(p)
    goleadas.sort(key=lambda p: (-p.saldo, -p.gols_usuario))
    campeoes = (User.objects.annotate(
        copas=Count('drafts_7a0', filter=Q(drafts_7a0__status='campeao'), distinct=True),
        invictos=Count('drafts_7a0', filter=Q(drafts_7a0__invicto=True), distinct=True),
    ).filter(copas__gt=0).order_by('-invictos', '-copas', 'first_name')[:10])
    return {'craques': craques, 'goleadas': goleadas[:10], 'campeoes': campeoes}


def visao(partida):
    """ Estado serializável para o front (sem expor nada além do jogo). """
    from futebol.escudos import escudo_url
    e = partida.estado
    lados = {}
    for lado in engine.LADOS:
        l = e['lados'][lado]
        time = {'elenco': l.get('elenco') or dados.obter(l['time'])['elenco'], 'nome': l.get('nome_time') or dados.obter(l['time'])['nome'],
                'ano': l.get('ano') or dados.obter(l['time'])['ano'], 'cor': l.get('cor') or dados.obter(l['time'])['cor'],
                'clube': l.get('clube') or dados.obter(l['time'])['clube']}
        jog = []
        for n in l['titulares']:
            j = next(x for x in time['elenco'] if x['nome'] == n)
            jog.append({'nome': n, 'pos': j['pos'], 'nota_base': j['nota'], 'nota': e['notas'].get(n, 6.0),
                        'expulso': n in l['expulsos'], 'lesionado': n in l['lesionados'],
                        'amarelo': l['amarelos'].get(n, 0)})
        banco = [{'nome': n, 'pos': next(x for x in time['elenco'] if x['nome'] == n)['pos'],
                  'nota_base': next(x for x in time['elenco'] if x['nome'] == n)['nota']} for n in l['banco']]
        lados[lado] = {'chave': l['time'], 'nome': time['nome'], 'ano': time['ano'], 'cor': time['cor'], 'escudo': escudo_url(time['clube']) or '',
                       'formacao': l['formacao'], 'mentalidade': l['mentalidade'], 'estilo': l['estilo'], 'subs': l['subs'],
                       'titulares': jog, 'banco': banco, 'forca': dados.forcas(engine.em_campo(e, lado))}
    r = engine.resumo(e)
    return {'id': partida.pk, 'status': e['status'], 'minuto': engine.minuto_texto(e), 'periodo': e['periodo'], 't': e['minuto'],
            'placar': e['placar'], 'lado_usuario': partida.lado_usuario, 'lados': lados, 'stats': r['stats'],
            'craque': r['craque'], 'nota_craque': r['nota_craque'], 'modo': partida.modo,
            'penaltis': e.get('penaltis'), 'mata_mata': e.get('mata_mata', False), 'vencedor': engine.vencedor(e),
            'resultado': partida.resultado, 'premio': partida.premio, 'total_eventos': len(e['eventos'])}

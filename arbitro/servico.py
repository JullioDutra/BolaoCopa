"""Regras de negócio do Apito Final: criar partida, servir o lance, VAR, responder, finalizar, premiar e ranking."""
import secrets

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Max, Q, Sum
from django.utils import timezone

from accounts import coins

from . import engine
from .models import PartidaArbitro

LIMITE_PREMIADAS_POR_DIA = 5


class ErroJogo(Exception):
    pass


def criar_partida(usuario):
    aberta = PartidaArbitro.objects.filter(usuario=usuario, status='andamento').first()
    if aberta:
        return aberta
    ultima = PartidaArbitro.objects.filter(usuario=usuario).first()
    vistos = [l['chave'] for l in ultima.lances if l.get('historico')] if ultima else []
    semente = secrets.randbits(48)
    return PartidaArbitro.objects.create(usuario=usuario, semente=semente,
                                         lances=engine.gerar_partida(semente, evitar=vistos))


def placar(partida):
    return {'indice': partida.indice, 'total': partida.total, 'pontos': partida.pontos,
            'acertos': partida.acertos, 'sequencia': partida.sequencia, 'status': partida.status}


def lance_atual(partida):
    """ Dados públicos do lance da vez; o relógio do bônus de tempo começa na primeira vez que ele é servido. """
    if partida.status == 'fim':
        return {'fim': True, 'placar': placar(partida), 'resumo': resumo(partida)}
    if partida.inicio_lance is None:
        partida.inicio_lance = timezone.now()
        partida.save(update_fields=['inicio_lance'])
    lance = partida.lances[partida.indice]
    return {'fim': False, 'lance': engine.publico(lance, partida.indice, partida.total), 'placar': placar(partida),
            'var_usado': partida.var_usado, 'var': engine.var_publico(lance) if partida.var_usado else None}


@transaction.atomic
def chamar_var(partida_id, usuario):
    partida = PartidaArbitro.objects.select_for_update().get(pk=partida_id, usuario=usuario)
    if partida.status == 'fim':
        raise ErroJogo('A partida já terminou.')
    if not partida.var_usado:
        partida.var_usado = True
        partida.vars_chamados += 1
        partida.save(update_fields=['var_usado', 'vars_chamados'])
    return engine.var_publico(partida.lances[partida.indice])


@transaction.atomic
def responder(partida_id, usuario, indice, resposta):
    partida = PartidaArbitro.objects.select_for_update().get(pk=partida_id, usuario=usuario)
    if partida.status == 'fim':
        raise ErroJogo('A partida já terminou.')
    if indice != partida.indice:
        raise ErroJogo('Esse lance já foi apitado.')
    lance = partida.lances[partida.indice]
    inicio = partida.inicio_lance or timezone.now()
    tempo_ms = (timezone.now() - inicio).total_seconds() * 1000 - lance['anim_ms']
    try:
        nota = engine.avaliar(lance, resposta, tempo_ms, partida.var_usado, partida.sequencia)
    except engine.RespostaInvalida as e:
        raise ErroJogo(str(e))

    partida.sequencia = partida.sequencia + 1 if nota['acertou'] else 0
    partida.melhor_sequencia = max(partida.melhor_sequencia, partida.sequencia)
    partida.acertos += 1 if nota['acertou'] else 0
    partida.pontos += nota['pontos']
    partida.respostas = partida.respostas + [{
        'chave': lance['chave'], 'resposta': nota['resposta'], 'acertou': nota['acertou'], 'parcial': nota['parcial'],
        'pontos': nota['pontos'], 'var': partida.var_usado, 'tempo_ms': max(0, int(tempo_ms)),
    }]
    partida.indice += 1
    partida.inicio_lance = None
    partida.var_usado = False
    fim = partida.indice >= partida.total
    if fim:
        _finalizar(partida)
    partida.save()
    if fim:
        _pos_jogo(partida)
    return {
        **nota, 'gabarito': lance['correta'], 'correta': engine.rotulos_corretos(lance), 'explicacao': lance['explicacao'],
        'var': engine.var_publico(lance), 'placar': placar(partida), 'fim': fim,
        'resumo': resumo(partida) if fim else None,
    }


def _finalizar(partida):
    partida.status = 'fim'
    partida.finalizado_em = timezone.now()
    premio = engine.premio(partida.acertos)
    hoje = timezone.localdate()
    premiadas_hoje = PartidaArbitro.objects.filter(usuario=partida.usuario, premio__gt=0,
                                                   finalizado_em__date=hoje).exclude(pk=partida.pk).count()
    if premio and premiadas_hoje < LIMITE_PREMIADAS_POR_DIA:
        partida.premio = premio
        coins.creditar(partida.usuario, premio, f'🟨 Apito Final: {partida.acertos}/{partida.total} acertos, {partida.pontos} pts')


def _pos_jogo(partida):
    try:
        from avisos import atividade, conquistas
        if partida.acertos == partida.total:
            atividade.registrar(partida.usuario, 'geral',
                                f'{atividade.nome_publico(partida.usuario)} acertou todos os lances no Apito Final '
                                f'({partida.pontos} pts)', url='/arbitro/')
        conquistas.checar(partida.usuario)
    except Exception:
        pass


def resumo(partida):
    titulo = engine.titulo_arbitro(partida.acertos)
    return {'pontos': partida.pontos, 'acertos': partida.acertos, 'total': partida.total, 'premio': partida.premio,
            'melhor_sequencia': partida.melhor_sequencia, 'titulo': titulo['nome'], 'icone': titulo['icone'],
            'recorde': recorde(partida.usuario) == partida.pontos and partida.pontos > 0}


def recorde(usuario):
    return PartidaArbitro.objects.filter(usuario=usuario, status='fim').aggregate(m=Max('pontos'))['m'] or 0


def sumula(partida):
    """ Lance a lance, para a tela de resultado. """
    linhas = []
    for i, resp in enumerate(partida.respostas):
        lance = partida.lances[i]
        rotulo, icone = engine.CATEGORIAS[lance['categoria']]
        escolhidas = []
        for g in lance['grupos']:
            opcoes = dict(map(tuple, g['opcoes']))
            escolhidas.append(opcoes.get(resp['resposta'].get(g['id']), '-'))
        linhas.append({'n': i + 1, 'titulo': lance['titulo'], 'categoria': rotulo, 'icone': icone,
                       'historico': lance['historico'], 'minha': ' + '.join(escolhidas),
                       'certa': ' + '.join(c['resposta'] for c in engine.rotulos_corretos(lance)),
                       'explicacao': lance['explicacao'], **resp})
    return linhas


def ranking():
    """ Quadro de honra: recorde, precisão e apitos de ouro. """
    fim = Q(partidas_arbitro__status='fim')
    base = User.objects.annotate(
        partidas=Count('partidas_arbitro', filter=fim),
        recorde=Max('partidas_arbitro__pontos', filter=fim),
        total_acertos=Sum('partidas_arbitro__acertos', filter=fim),
        ouros=Count('partidas_arbitro', filter=fim & Q(partidas_arbitro__acertos=engine.LANCES_POR_PARTIDA)),
    ).filter(partidas__gt=0).select_related('perfil')
    recordistas = list(base.order_by('-recorde', '-ouros', 'first_name')[:15])
    precisos = []
    for u in base.filter(partidas__gte=3):
        u.precisao = round(100 * (u.total_acertos or 0) / (u.partidas * engine.LANCES_POR_PARTIDA))
        precisos.append(u)
    precisos.sort(key=lambda u: (-u.precisao, -u.partidas))
    ouro = [u for u in base.filter(ouros__gt=0).order_by('-ouros', '-recorde')[:10]]
    return {'recordistas': recordistas, 'precisos': precisos[:10], 'ouro': ouro}


def numeros_usuario(usuario):
    fim = PartidaArbitro.objects.filter(usuario=usuario, status='fim')
    agg = fim.aggregate(n=Count('id'), recorde=Max('pontos'), acertos=Sum('acertos'))
    n = agg['n'] or 0
    return {'partidas': n, 'recorde': agg['recorde'] or 0,
            'precisao': round(100 * (agg['acertos'] or 0) / (n * engine.LANCES_POR_PARTIDA)) if n else 0,
            'ouros': fim.filter(acertos=engine.LANCES_POR_PARTIDA).count()}

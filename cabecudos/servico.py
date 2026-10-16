"""Regras do Cabeçudos: iniciar partida (token), validar e registrar o resultado, progresso e ranking."""
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Max, Q, Sum
from django.utils import timezone

from accounts import coins

from .fases import DURACAO_S, FASES, MAX_GOLS, TOLERANCIA_S, premio
from .models import PartidaCabecudos

LIMITE_PREMIADAS_POR_DIA = 10


class ErroJogo(Exception):
    pass


def fase_liberada(usuario):
    """ Maior fase que o usuário pode jogar: 1 + a maior fase já vencida (até a última). """
    venceu = PartidaCabecudos.objects.filter(usuario=usuario, status='vitoria').aggregate(m=Max('fase'))['m'] or 0
    return min(len(FASES), venceu + 1)


def iniciar(usuario, fase):
    try:
        fase = int(fase)
    except (TypeError, ValueError):
        raise ErroJogo('Fase inválida.')
    if not 1 <= fase <= fase_liberada(usuario):
        raise ErroJogo('Essa fase ainda está bloqueada.')
    # partida abandonada vira derrota: não dá para fugir de um jogo perdido e recomeçar sem custo
    PartidaCabecudos.objects.filter(usuario=usuario, status='jogando').update(status='derrota', finalizada_em=timezone.now())
    p = PartidaCabecudos.objects.create(usuario=usuario, fase=fase)
    return p, {**FASES[fase - 1], 'fase': fase, 'total_fases': len(FASES), 'duracao': DURACAO_S, 'token': str(p.token)}


def finalizar(usuario, token, gols_pro, gols_contra):
    with transaction.atomic():
        resultado = _finalizar(usuario, token, gols_pro, gols_contra)
    if resultado is None:       # marcada como inválida (já salvo): avisa depois de confirmar a transação
        raise ErroJogo('Resultado não confere com o relógio da partida.')
    return resultado


def _finalizar(usuario, token, gols_pro, gols_contra):
    try:
        p = PartidaCabecudos.objects.select_for_update().get(token=token, usuario=usuario)
    except Exception:  # token malformado (ValidationError), de outro usuário ou inexistente
        raise ErroJogo('Partida não encontrada.')
    if p.status != 'jogando':
        raise ErroJogo('Essa partida já foi encerrada.')
    try:
        gp, gc = int(gols_pro), int(gols_contra)
    except (TypeError, ValueError):
        raise ErroJogo('Placar inválido.')
    duracao = (timezone.now() - p.iniciada_em).total_seconds()
    p.finalizada_em = timezone.now()
    plausivel = 0 <= gp <= MAX_GOLS and 0 <= gc <= MAX_GOLS and DURACAO_S - TOLERANCIA_S <= duracao <= 60 * 30
    if not plausivel:
        p.status = 'invalida'
        p.save()
        return None
    p.gols_pro, p.gols_contra = gp, gc
    p.status = 'vitoria' if gp > gc else 'empate' if gp == gc else 'derrota'
    hoje = timezone.localdate()
    premiadas = PartidaCabecudos.objects.filter(usuario=usuario, premio__gt=0, finalizada_em__date=hoje).count()
    valor = premio(p.fase, p.status)
    if valor and premiadas < LIMITE_PREMIADAS_POR_DIA:
        p.premio = valor
        coins.creditar(usuario, valor, f"⚽ Cabeçudos: {gp} x {gc} contra {FASES[p.fase - 1]['nome']}")
    p.save()
    if p.status == 'vitoria':
        try:
            from avisos import atividade, conquistas
            if p.fase == len(FASES):
                atividade.registrar(usuario, 'geral', f'{atividade.nome_publico(usuario)} venceu O Fenômeno e foi campeão do Cabeçudos!',
                                    url='/cabecudos/')
            conquistas.checar(usuario)
        except Exception:
            pass
    return {'status': p.status, 'gols_pro': gp, 'gols_contra': gc, 'premio': p.premio, 'fase': p.fase,
            'liberada': fase_liberada(usuario), 'total_fases': len(FASES)}


def numeros(usuario):
    fim = PartidaCabecudos.objects.filter(usuario=usuario).exclude(status__in=['jogando', 'invalida'])
    agg = fim.aggregate(v=Count('id', filter=Q(status='vitoria')), gols=Sum('gols_pro'), jogos=Count('id'))
    return {'vitorias': agg['v'] or 0, 'gols': agg['gols'] or 0, 'jogos': agg['jogos'] or 0,
            'titulos': fim.filter(status='vitoria', fase=len(FASES)).count(), 'liberada': fase_liberada(usuario)}


def ranking():
    ok = Q(partidas_cabecudos__status='vitoria')
    return (User.objects.annotate(fase_max=Max('partidas_cabecudos__fase', filter=ok),
                                  titulos_cab=Count('partidas_cabecudos', filter=ok & Q(partidas_cabecudos__fase=len(FASES))),
                                  gols_cab=Sum('partidas_cabecudos__gols_pro', filter=Q(partidas_cabecudos__status__in=['vitoria', 'empate', 'derrota'])))
            .filter(fase_max__isnull=False).order_by('-titulos_cab', '-fase_max', '-gols_cab')[:15])

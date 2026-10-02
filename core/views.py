from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from accounts import streak
from accounts.models import PerfilUsuario
from bolao.decorators import acesso_liberado_required
from palpites import api_futebol
from palpites.models import Jogo

from . import noticias


def _time_do_usuario(usuario):
    perfil = PerfilUsuario.objects.select_related('time_coracao').filter(usuario=usuario).first()
    return perfil.time_coracao if perfil else None


def _resenha_recente(limite=6):
    try:
        from avisos.atividade import icone
        from avisos.models import Atividade
        return [{'a': a, 'icone': icone(a.tipo)} for a in Atividade.objects.all()[:limite]]
    except DatabaseError:
        return []


@acesso_liberado_required
def dashboard_view(request):
    """
    Tela principal. O usuário só chega aqui se estiver logado
    e com a participação (resenha ou pix) devidamente aprovada.
    """
    proximo_jogo = Jogo.objects.filter(data_hora__gt=timezone.now()).order_by('data_hora').first()

    # Bônus diário / sequência de acessos (falha silenciosa se as tabelas novas ainda não existem)
    resultado_streak = None
    try:
        resultado_streak = streak.registrar_acesso(request.user)
    except DatabaseError:
        pass

    time = None
    jogo_do_time = None
    perfil = None
    try:
        perfil = PerfilUsuario.objects.select_related('time_coracao').filter(usuario=request.user).first()
        time = perfil.time_coracao if perfil else None
    except DatabaseError:
        pass
    if time:
        jogo_do_time = (
            Jogo.objects.filter(finalizado=False, data_hora__gt=timezone.now() - timedelta(hours=3))
            .filter(Q(time_casa=time.nome) | Q(time_fora=time.nome))
            .order_by('data_hora').first()
        )

    context = {
        'participacao': request.user.participacao,
        'proximo_jogo': proximo_jogo,
        'streak_resultado': resultado_streak,
        'streak_atual': perfil.streak_dias if perfil else 0,
        'time_coracao': time,
        'jogo_do_time': jogo_do_time,
        'whatsapp_grupo': getattr(settings, 'WHATSAPP_GRUPO_URL', ''),
        'resenha': _resenha_recente(),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def feed_noticias(request):
    """ JSON com as notícias do time do coração (carregado por JS depois que a página abre). """
    time = _time_do_usuario(request.user)
    if not time:
        return JsonResponse({'time': None, 'noticias': []})
    return JsonResponse({'time': time.nome, 'noticias': noticias.buscar_noticias(time.nome)})


@login_required
def feed_tabela(request):
    """ JSON com a classificação do Brasileirão (top 5 + posição do time do usuário). """
    try:
        tabela = api_futebol.classificacao()
    except api_futebol.ApiIndisponivel:
        tabela = []
    time = _time_do_usuario(request.user)
    nome_time = time.nome if time else None
    linhas = tabela[:5]
    if nome_time and all(l['time'] != nome_time for l in linhas):
        extra = next((l for l in tabela if l['time'] == nome_time), None)
        if extra:
            linhas = linhas + [extra]
    return JsonResponse({'tabela': linhas, 'meu_time': nome_time})

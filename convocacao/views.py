from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
import datetime

from .models import Jogador, Convocacao, SelecaoBrasileirao
from .forms import SelecaoBrasileiraoForm
from bolao.decorators import acesso_liberado_required

# Data (aproximada) de abertura da Copa de 2030, para o cronômetro do mural.
PROXIMA_COPA = datetime.datetime(2030, 6, 13, 16, 0, 0)


# ==========================================
# MODO COPA — ENCERRADO (só exibição/histórico)
# ==========================================
@acesso_liberado_required
def copa_mural(request):
    """Substitui a antiga tela de montar seleção da Copa.
    Agora só mostra o campeão daquele modo e o cronômetro para 2030."""
    campeao = Convocacao.calcular_campeao()

    return render(request, 'convocacao/copa_mural.html', {
        'campeao': campeao,
        'proxima_copa_iso': PROXIMA_COPA.isoformat(),
    })


@acesso_liberado_required
def ranking_convocacao(request):
    """Ranking histórico do modo Copa (encerrado)."""
    oficiais = set(Jogador.objects.filter(convocado_oficial=True).values_list('id', flat=True))
    convocacoes = Convocacao.objects.select_related('usuario').all()

    ranking = []
    for conv in convocacoes:
        escolhidos = set(conv.jogadores.values_list('id', flat=True))
        acertos = len(oficiais.intersection(escolhidos))
        ranking.append({
            'usuario': conv.usuario,
            'acertos': acertos,
        })

    ranking.sort(key=lambda x: x['acertos'], reverse=True)

    return render(request, 'convocacao/ranking_convocacao.html', {
        'ranking': ranking,
        'total_oficiais': len(oficiais),
    })


@acesso_liberado_required
def estatisticas_convocacao(request):
    total_listas = Convocacao.objects.count()
    jogadores_mais_escalados = Jogador.objects.annotate(
        total_escalacoes=Count('convocados_copa')
    ).filter(total_escalacoes__gt=0).order_by('-total_escalacoes')

    dados_jogadores = []
    for jogador in jogadores_mais_escalados:
        porcentagem = (jogador.total_escalacoes / total_listas * 100) if total_listas > 0 else 0
        dados_jogadores.append({
            'jogador': jogador,
            'total_escalacoes': jogador.total_escalacoes,
            'porcentagem': round(porcentagem, 1),
            'acertou_oficial': jogador.convocado_oficial
        })

    return render(request, 'convocacao/mais_escalados.html', {
        'dados_jogadores': dados_jogadores,
        'total_listas': total_listas
    })


# ==========================================
# NOVO MODO: SELEÇÃO DO BRASILEIRÃO (4-3-3)
# ==========================================
@login_required
def montar_selecao(request):
    """Tela ativa para escalar o 4-3-3 do Brasileirão Série A."""
    selecao, created = SelecaoBrasileirao.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = SelecaoBrasileiraoForm(request.POST, instance=selecao)
        if form.is_valid():
            form.save()
            messages.success(request, "Seleção 4-3-3 do Brasileirão confirmada com sucesso! ⚽")
            return redirect('convocacao:montar_selecao')
    else:
        form = SelecaoBrasileiraoForm(instance=selecao)

    return render(request, 'convocacao/montar_selecao.html', {
        'form': form,
        'selecao': selecao,
    })


@acesso_liberado_required
def ranking_brasileirao(request):
    """Ranking do novo modo 4-3-3. Recalcula a pontuação de cada escalação na hora."""
    selecoes = SelecaoBrasileirao.objects.select_related('usuario').all()
    ranking = []
    for selecao in selecoes:
        pontos = selecao.calcular_pontuacao()
        ranking.append({'usuario': selecao.usuario, 'pontos': pontos})

    ranking.sort(key=lambda x: x['pontos'], reverse=True)

    return render(request, 'convocacao/ranking_brasileirao.html', {'ranking': ranking})

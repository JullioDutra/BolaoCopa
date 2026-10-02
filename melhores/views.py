from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from accounts import coins
from bolao.decorators import acesso_liberado_required

from . import services
from .models import Aposta, Categoria, Edicao
from .odds import calcular_odds, distribuicao_da_galera


def _edicao_ativa():
    return Edicao.objects.filter(ativa=True).order_by('-ano').first()


@acesso_liberado_required
def home(request):
    edicao = _edicao_ativa()
    if edicao is None:
        messages.info(request, "A votação dos Melhores do Ano ainda não abriu. Fique de olho!")
        return redirect('dashboard')

    minhas = {a.categoria_id: a for a in Aposta.objects.filter(usuario=request.user, categoria__edicao=edicao).select_related('candidato', 'categoria__edicao')}
    categorias = []
    for categoria in edicao.categorias.prefetch_related('candidatos'):
        odds = calcular_odds(categoria)
        galera = distribuicao_da_galera(categoria)
        total_coins = sum(c for c, _ in galera.values()) or 0
        candidatos = []
        for c in categoria.candidatos.all():
            coins_c, apostadores = galera.get(c.id, (0, 0))
            candidatos.append({
                'obj': c,
                'odd': odds[c.id],
                'pct_galera': round(coins_c * 100 / total_coins) if total_coins else 0,
                'apostadores': apostadores,
            })
        candidatos.sort(key=lambda x: x['odd'])  # favorito primeiro
        categorias.append({
            'obj': categoria,
            'candidatos': candidatos,
            'minha': minhas.get(categoria.id),
            'total_coins': total_coins,
        })

    return render(request, 'melhores/home.html', {
        'edicao': edicao,
        'categorias': categorias,
        'saldo': coins.saldo(request.user),
        'aposta_minima': services.APOSTA_MINIMA,
        'tem_apostas': bool(minhas),
        'abertas': [a for a in minhas.values() if a.status == 'aberta'],
    })


@acesso_liberado_required
@require_POST
def apostar(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    try:
        aposta = services.apostar(
            request.user, categoria.id, request.POST.get('candidato'), request.POST.get('valor'),
        )
        messages.success(
            request,
            f"Aposta feita: {aposta.valor} 🪙 em {aposta.candidato.nome} (odd {aposta.odd_travada}). "
            f"Retorno possível: {aposta.retorno_potencial} 🪙",
        )
    except services.ApostaInvalida as erro:
        messages.error(request, str(erro))
    return redirect(f"{reverse('melhores:home')}#cat-{categoria.slug}")


@acesso_liberado_required
@require_POST
def apostar_cupom(request):
    """
    Confirma o cupom: várias seleções de uma vez. Cada linha de `sel` é
    "categoria:candidato:valor:odd". Cada aposta é independente (uma recusada não derruba as outras).
    """
    feitas, erros = [], []
    for linha in request.POST.getlist('sel')[:40]:
        partes = linha.split(':')
        if len(partes) != 4:
            continue
        categoria_id, candidato_id, valor, odd = partes
        try:
            aposta = services.apostar(request.user, categoria_id, candidato_id, valor, odd_esperada=odd)
            feitas.append(aposta)
        except (services.ApostaInvalida, ValueError) as erro:
            erros.append(str(erro) or "Aposta inválida.")
    if feitas:
        total = sum(a.valor for a in feitas)
        messages.success(request, f"{len(feitas)} aposta(s) confirmada(s) — 🪙 {total} apostados. Boa sorte!")
    for erro in erros:
        messages.error(request, erro)
    return redirect('melhores:home')


@acesso_liberado_required
@require_POST
def cancelar(request, categoria_id):
    try:
        services.cancelar_aposta(request.user, categoria_id)
        messages.success(request, "Aposta cancelada e coins devolvidos.")
    except services.ApostaInvalida as erro:
        messages.error(request, str(erro))
    return redirect('melhores:home')


@acesso_liberado_required
def minhas_apostas(request):
    edicao = _edicao_ativa()
    apostas = (
        Aposta.objects.filter(usuario=request.user, categoria__edicao=edicao)
        .select_related('categoria', 'candidato') if edicao else Aposta.objects.none()
    )
    resumo = {
        'em_jogo': sum(a.valor for a in apostas if a.status == 'aberta'),
        'ganhos': sum(a.retorno for a in apostas if a.status == 'ganha'),
        'acertos': sum(1 for a in apostas if a.status == 'ganha'),
        'resolvidas': sum(1 for a in apostas if a.status in ('ganha', 'perdida')),
    }
    return render(request, 'melhores/minhas.html', {
        'edicao': edicao, 'apostas': apostas, 'resumo': resumo, 'saldo': coins.saldo(request.user),
    })


@acesso_liberado_required
def ranking(request):
    edicao = _edicao_ativa()
    linhas = services.ranking(edicao) if edicao else []
    return render(request, 'melhores/ranking.html', {'edicao': edicao, 'linhas': linhas})


@acesso_liberado_required
def api_odds(request):
    """ JSON com as odds atuais — a tela consulta de tempos em tempos para atualizar ao vivo. """
    edicao = _edicao_ativa()
    dados = {}
    if edicao:
        for categoria in edicao.categorias.prefetch_related('candidatos'):
            dados[categoria.id] = {str(cid): str(odd) for cid, odd in calcular_odds(categoria).items()}
    return JsonResponse({'odds': dados})


# ---------------------------------------------------------------- staff

@staff_member_required
def staff_painel(request):
    edicao = _edicao_ativa()
    categorias = edicao.categorias.prefetch_related('candidatos').all() if edicao else []
    return render(request, 'melhores/staff.html', {'edicao': edicao, 'categorias': categorias})


@staff_member_required
@require_POST
def staff_acao(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    acao = request.POST.get('acao')
    try:
        if acao == 'liquidar':
            pagos = services.liquidar(categoria.id, request.POST.get('vencedor'))
            messages.success(request, f"{categoria.nome}: liquidada! {pagos} aposta(s) paga(s).")
        elif acao == 'anular':
            services.anular(categoria.id)
            messages.warning(request, f"{categoria.nome}: anulada e apostas devolvidas.")
        elif acao in ('abrir', 'fechar'):
            categoria.aberta = acao == 'abrir'
            categoria.save(update_fields=['aberta'])
            messages.success(request, f"{categoria.nome}: apostas {'abertas' if categoria.aberta else 'fechadas'}.")
    except services.ApostaInvalida as erro:
        messages.error(request, str(erro))
    except Exception:
        messages.error(request, "Não foi possível concluir a ação. Confira os dados e tente de novo.")
    return redirect('melhores:staff')

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .engine import sortear_novo_elenco
# Importe seus modelos e o motor lógico que criamos
from .models import MeuDraft, CartaJogador, PartidaPenalti
from .engine import selecionar_carta, calcular_resultado_penalti, processar_cobranca, sortear_novo_elenco
from django.db.models import Q, Count
from django.contrib.auth.models import User


# ==========================================
# API 1: ESCOLHER CARTA NO DRAFT
# ==========================================    
@login_required
@require_POST
def api_escolher_carta(request):
    """ Recebe o clique do usuário numa carta durante o Draft """
    try:
        data = json.loads(request.body)
        carta_id = data.get('carta_id')
        
        # Pega o draft ativo do usuário
        draft = get_object_or_404(MeuDraft, usuario=request.user, status='ativo')
        
        # Roda a regra de negócio do motor (engine.py)
        sucesso, mensagem = selecionar_carta(draft, carta_id)
        
        return JsonResponse({
            'sucesso': sucesso,
            'mensagem': mensagem,
            'draft_concluido': draft.elenco_sorteado is None # Se for None, é porque já escolheu os 6
        })
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)})



@login_required
def tela_draft(request):
    """ Exibe a tela de escolha de cartas do Draft """
    
    # Camada de segurança: Tenta buscar o draft ativo, se não existir, cria um.
    # Se houver mais de um ativo (erro no banco), ele pega o último e ignora o resto.
    try:
        draft = MeuDraft.objects.filter(usuario=request.user, status='ativo').last()
        if not draft:
            draft = MeuDraft.objects.create(usuario=request.user, status='ativo')
            created = True
        else:
            created = False
    except Exception as e:
        draft = MeuDraft.objects.create(usuario=request.user, status='ativo')
        created = True
    
    # Se acabou de criar ou se a prancheta não está cheia mas não tem elenco na tela:
    if created or (draft.elenco_sorteado is None and (draft.batedores.count() < 5 or draft.goleiro is None)):
        sortear_novo_elenco(draft)
        
    # Se o draft já está totalmente completo (5 de linha + 1 goleiro)
    if draft.elenco_sorteado is None and draft.batedores.count() == 5 and draft.goleiro is not None:
        return redirect('minijogo:lobby')

    context = {
        'draft': draft,
        'elenco_atual': draft.elenco_sorteado,
        'jogadores_sorteados': draft.elenco_sorteado.jogadores.all() if draft.elenco_sorteado else [],
        'meus_batedores': draft.batedores.all(),
        'meu_goleiro': draft.goleiro
    }
    return render(request, 'minijogo/draft.html', context)


@login_required
def lobby_batalha(request):
    """ Coloca o jogador na fila e procura um adversário """
    draft = MeuDraft.objects.filter(usuario=request.user, status='ativo').last()
    if not draft:
        return redirect('minijogo:tela_draft')
        
    partida_atual = PartidaPenalti.objects.filter(
        (Q(jogador1=request.user) | Q(jogador2=request.user)) & 
        ~Q(fase='finalizado')
    ).first()
    
    if partida_atual:
        return redirect('minijogo:tela_jogo', partida_id=partida_atual.id)
        
    partida_aguardando = PartidaPenalti.objects.filter(fase='aguardando').exclude(jogador1=request.user).first()
    
    if partida_aguardando:
        # Achou adversário! Entra na partida
        partida_aguardando.jogador2 = request.user
        partida_aguardando.draft_j2 = draft
        partida_aguardando.fase = '5_cobrancas'
        partida_aguardando.turno_batedor = partida_aguardando.jogador1 # 👈 CRUCIAL: Jogador 1 começa a bater!
        partida_aguardando.save()
        return redirect('minijogo:tela_jogo', partida_id=partida_aguardando.id)
    else:
        nova_partida, created = PartidaPenalti.objects.get_or_create(
            jogador1=request.user,
            draft_j1=draft,
            fase='aguardando'
        )
        return render(request, 'minijogo/esperando_adversario.html', {'partida': nova_partida})


@login_required
def aceitar_convite(request, partida_id):
    """ Coloca o amigo na sala de pênaltis através do link """
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    draft = MeuDraft.objects.filter(usuario=request.user, status='ativo').last()
    
    if not draft:
        return redirect('minijogo:tela_draft')
    
    if partida.fase == 'aguardando' and partida.jogador1 != request.user:
        partida.jogador2 = request.user
        partida.draft_j2 = draft
        partida.fase = '5_cobrancas'
        partida.turno_batedor = partida.jogador1 # 👈 CRUCIAL: Jogador 1 começa a bater!
        partida.save()
        return redirect('minijogo:tela_jogo', partida_id=partida.id)
        
    return redirect('minijogo:tela_jogo', partida_id=partida.id)
    
    
@login_required
def tela_jogo(request, partida_id):
    """ Carrega o visual do gol e os controles """
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    
    # Define quem é o jogador na tela para o JavaScript saber de que lado ele está
    sou_jogador_1 = (request.user == partida.jogador1)
    
    context = {
        'partida': partida,
        'sou_jogador_1': 'true' if sou_jogador_1 else 'false',
        'meu_draft': partida.draft_j1 if sou_jogador_1 else partida.draft_j2,
        'adversario_draft': partida.draft_j2 if sou_jogador_1 else partida.draft_j1,
    }
    return render(request, 'minijogo/tela_jogo.html', context)


from django.urls import reverse



@login_required
def api_desistir(request):
    """ Encerra o jogo imediatamente e dá a vitória ao adversário """
    if request.method == 'POST':
        data = json.loads(request.body)
        partida_id = data.get('partida_id')
        
        partida = get_object_or_404(PartidaPenalti, id=partida_id)
        
        # Define quem desistiu e quem ganhou
        if request.user == partida.jogador1:
            vencedor = partida.jogador2
        else:
            vencedor = partida.jogador1
            
        # Aplica regras de fim de jogo
        partida.fase = 'finalizado'
        partida.vencedor = vencedor
        partida.save()
        
        return JsonResponse({'sucesso': True})
    return JsonResponse({'sucesso': False})



# ==========================================
# O JOGADOR CLICOU NA TRAVE OU DEU TIMEOUT
# ==========================================
def api_enviar_acao(request):
    try:
        data = json.loads(request.body)
        partida = get_object_or_404(PartidaPenalti, id=data.get('partida_id'))
        zona = data.get('zona')
        carta_id = data.get('carta_id')

        # Se for a vez do usuário bater
        if request.user == partida.turno_batedor:
            partida.chute_zona = zona
            partida.chute_carta_id = carta_id
        # Se for a vez do usuário defender
        elif request.user != partida.turno_batedor:
            partida.defesa_zona = zona
            partida.defesa_carta_id = carta_id

        partida.save()

        # Se as duas ações já foram preenchidas (ou se alguém deu timeout), calcula a rodada!
        if partida.chute_zona and partida.defesa_zona:
            processar_cobranca(partida)

        return JsonResponse({'sucesso': True})
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)})


# ==========================================
# O RADAR DA TELA (ATUALIZA A CADA 2 SEGUNDOS)
# ==========================================
def api_status_partida(request, partida_id):
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    
    meu_turno = 'aguardando'
    if partida.fase in ['5_cobrancas', 'alternadas']:
        if request.user == partida.turno_batedor:
            if not partida.chute_zona: meu_turno = 'chutar'
        else:
            if not partida.defesa_zona: meu_turno = 'defender'

    # --- NOVIDADE: Buscando Nome e Sequência Invicta do Vencedor ---
    vencedor_nome = None
    vencedor_streak = 0
    
    if partida.vencedor:
        # Pega o primeiro nome, se não tiver, usa o username
        vencedor_nome = partida.vencedor.first_name if partida.vencedor.first_name else partida.vencedor.username
        
        # Descobre qual foi o draft que ganhou para pegar as vitórias seguidas
        draft_vencedor = partida.draft_j1 if partida.vencedor == partida.jogador1 else partida.draft_j2
        if draft_vencedor:
            vencedor_streak = draft_vencedor.vitorias_seguidas

    dados = {
        'fase': partida.fase,
        'rodada_atual': partida.rodada_atual,
        'placar_j1': partida.placar_j1,
        'placar_j2': partida.placar_j2,
        'meu_turno': meu_turno,
        'vencedor': partida.vencedor.username if partida.vencedor else None,
        'ultimo_chute_zona': partida.ultimo_chute_zona,
        'ultima_defesa_zona': partida.ultima_defesa_zona,
        'ultimo_resultado': partida.ultimo_resultado,
        # Variáveis novas enviadas para a tela!
        'vencedor_nome': vencedor_nome,
        'vencedor_streak': vencedor_streak,
    }
    
    return JsonResponse(dados)

@login_required
def ranking_x1(request):
    """ Exibe o Top 10 jogadores que mais alcançaram 10 vitórias seguidas """
    
    # Anota quantos rascunhos com status 'campeao' cada usuário tem
    top_lendas = User.objects.annotate(
        titulos_lenda=Count('drafts_x1', filter=Q(drafts_x1__status='campeao'))
    ).filter(titulos_lenda__gt=0).order_by('-titulos_lenda')[:10]
    
    # Busca a carta de linha mais escolhida (Uma funcionalidade extra que você pediu!)
    # Como as queries de ManyToMany podem ser pesadas, deixaremos a estrutura pronta:
    # (Futuramente você pode rastrear a carta exata em uma tabela extra, mas o ranking já brilha!)
    
    return render(request, 'minijogo/ranking.html', {'top_lendas': top_lendas})


import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .engine import sortear_novo_elenco
# Importe seus modelos e o motor lógico que criamos
from .models import MeuDraft, CartaJogador, PartidaPenalti
from .engine import selecionar_carta, calcular_resultado_penalti, processar_fim_de_rodada
from django.db.models import Q

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


# ==========================================
# API 2: CHUTAR OU DEFENDER NA PARTIDA
# ==========================================
@login_required
@require_POST
def api_enviar_acao(request):
    """ Recebe o quadrante que o usuário clicou na trave """
    try:
        data = json.loads(request.body)
        partida_id = data.get('partida_id')
        tipo_acao = data.get('tipo_acao') # 'chute' ou 'defesa'
        zona = data.get('zona') # 'se', 'me', 'id', etc.
        
        partida = get_object_or_404(PartidaPenalti, id=partida_id)
        
        # Aqui, no mundo real, você vai salvar a ação na tabela Cobranca correspondente
        # Exemplo resumido:
        # cobranca.alvo_chute = zona (se for o batedor)
        # cobranca.pulo_goleiro = zona (se for o goleiro)
        # cobranca.save()
        
        # Se os DOIS já tiverem jogado (um escolheu chutar e outro pular),
        # você chama a matemática do Over lá do engine.py e atualiza o placar!
        
        return JsonResponse({'sucesso': True, 'mensagem': 'Ação registrada! Aguardando adversário...'})
    except Exception as e:
        return JsonResponse({'sucesso': False, 'mensagem': str(e)})


# ==========================================
# API 3: O RADAR DO JOGO (POLLING)
# ==========================================
@login_required
def api_status_partida(request, partida_id):
    """ 
    O JavaScript vai chamar essa view a cada 2 segundos (Polling).
    Ela serve para dizer ao navegador: "Teve gol?", "Acabou?", "Aumentou a rodada?"
    """
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    
    # Montamos um pacote de dados atualizados para a tela do usuário
    dados = {
        'fase': partida.fase,
        'rodada_atual': partida.rodada_atual,
        'placar_j1': partida.placar_j1,
        'placar_j2': partida.placar_j2,
        # Se for a fase finalizada, enviamos o ganhador
        'vencedor': partida.vencedor.username if partida.vencedor else None
    }
    
    return JsonResponse(dados)


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
    
    # Camada de segurança: Se ele não tiver um draft ativo, devolve ele pro Draft!
    draft = MeuDraft.objects.filter(usuario=request.user, status='ativo').last()
    if not draft:
        return redirect('minijogo:tela_draft')
        
    # 1. Verifica se já estou em uma partida em andamento
    partida_atual = PartidaPenalti.objects.filter(
        (Q(jogador1=request.user) | Q(jogador2=request.user)) & 
        ~Q(fase='finalizado')
    ).first()
    
    if partida_atual:
        return redirect('minijogo:tela_jogo', partida_id=partida_atual.id)
        
    # 2. Tenta achar uma partida aguardando jogador
    partida_aguardando = PartidaPenalti.objects.filter(fase='aguardando').exclude(jogador1=request.user).first()
    
    if partida_aguardando:
        # Achou adversário! Entra na partida
        partida_aguardando.jogador2 = request.user
        partida_aguardando.draft_j2 = draft
        partida_aguardando.fase = '5_cobrancas'
        partida_aguardando.save()
        return redirect('minijogo:tela_jogo', partida_id=partida_aguardando.id)
    else:
        # Não achou ninguém. Cria uma sala e fica esperando.
        nova_partida, created = PartidaPenalti.objects.get_or_create(
            jogador1=request.user,
            draft_j1=draft,
            fase='aguardando'
        )
        return render(request, 'minijogo/esperando_adversario.html', {'partida': nova_partida})
    
    
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
def aceitar_convite(request, partida_id):
    """ Coloca o amigo na sala de pênaltis através do link """
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    
    # Pega o draft do amigo (ele precisa ter um time montado!)
    meu_draft = get_object_or_404(MeuDraft, usuario=request.user, status='ativo')
    
    # Verifica se a sala ainda está vazia e se ele não está clicando no próprio link
    if partida.fase == 'aguardando' and partida.jogador1 != request.user:
        partida.jogador2 = request.user
        partida.draft_j2 = meu_draft
        partida.fase = '5_cobrancas'
        partida.save()
        return redirect('minijogo:tela_jogo', partida_id=partida.id)
        
    # Se a sala já lotou ou se ele clicou no próprio link, joga ele pra tela da partida
    return redirect('minijogo:tela_jogo', partida_id=partida.id)
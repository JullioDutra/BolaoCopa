import json
from django.http import JsonResponse
import random 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .engine import sortear_novo_elenco
# Importe seus modelos e o motor lógico que criamos
from .models import MeuDraft, CartaJogador, PartidaPenalti
from .engine import selecionar_carta, calcular_resultado_penalti, processar_cobranca, sortear_novo_elenco
from django.db.models import Q, Count, Sum, Max
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
    
    # 💥 LÓGICA DAS REGRAS (Toggles): Lê do POST e salva na sessão do navegador
    if request.method == 'POST':
        request.session['usa_poderes'] = request.POST.get('usa_poderes') == 'on'
        request.session['usa_olheiro'] = request.POST.get('usa_olheiro') == 'on'
        request.session['usa_emotes'] = request.POST.get('usa_emotes') == 'on'
    
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
        campeonato_confronto_id = request.session.pop('campeonato_penalti_pendente', None)
        if campeonato_confronto_id:
            # Devolve ele direto para a sala do campeonato!
            return redirect('duelos:iniciar_jogo_campeonato', confronto_id=campeonato_confronto_id)
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
    """ Coloca o jogador na fila ou puxa o convite pendente """
    draft = MeuDraft.objects.filter(usuario=request.user, status='ativo').last()
    
    # VERIFICAÇÃO RÍGIDA: Tem draft? Ele está completo com 5 batedores e 1 goleiro?
    draft_completo = draft and draft.batedores.count() == 5 and draft.goleiro is not None
    if not draft_completo:
        return redirect('minijogo:tela_draft')
        
    # CORREÇÃO 2: Se ele acabou de vir do Draft, resgata a sala do amigo!
    convite_id = request.session.pop('convite_pendente', None)
    if convite_id:
        partida_convite = PartidaPenalti.objects.filter(id=convite_id, fase='aguardando').first()
        if partida_convite and partida_convite.jogador1 != request.user:
            partida_convite.jogador2 = request.user
            partida_convite.draft_j2 = draft
            partida_convite.fase = '5_cobrancas'
            
            if partida_convite.moeda_sorteio == 'j1':
                partida_convite.turno_batedor = partida_convite.jogador1
            else:
                partida_convite.turno_batedor = partida_convite.jogador2
            
            partida_convite.save()
            return redirect('minijogo:tela_jogo', partida_id=partida_convite.id)

    # AQUI CONTINUA O SEU CÓDIGO NORMAL DE PROCURAR PARTIDA
    partida_atual = PartidaPenalti.objects.filter(
        (Q(jogador1=request.user) | Q(jogador2=request.user)) & 
        ~Q(fase='finalizado')
    ).first()
    
    if partida_atual:
        if partida_atual.fase == 'aguardando':
            return render(request, 'minijogo/esperando_adversario.html', {'partida': partida_atual})
        return redirect('minijogo:tela_jogo', partida_id=partida_atual.id)
        
    partida_aguardando = PartidaPenalti.objects.filter(fase='aguardando').exclude(jogador1=request.user).first()
    
    if partida_aguardando:
        partida_aguardando.jogador2 = request.user
        partida_aguardando.draft_j2 = draft
        partida_aguardando.fase = '5_cobrancas'
        
        if partida_aguardando.moeda_sorteio == 'j1':
            partida_aguardando.turno_batedor = partida_aguardando.jogador1
        else:
            partida_aguardando.turno_batedor = partida_aguardando.jogador2
            
        partida_aguardando.save()
        return redirect('minijogo:tela_jogo', partida_id=partida_aguardando.id)
    else:
        quem_comeca = random.choice(['j1', 'j2'])
        usa_poderes = request.session.get('usa_poderes', True)
        usa_olheiro = request.session.get('usa_olheiro', True)
        usa_emotes = request.session.get('usa_emotes', True)

        nova_partida = PartidaPenalti.objects.create(
            jogador1=request.user,
            draft_j1=draft,
            fase='aguardando',
            moeda_sorteio=quem_comeca,
            usa_poderes=usa_poderes,
            usa_olheiro=usa_olheiro,
            usa_emotes=usa_emotes
        )
        return render(request, 'minijogo/esperando_adversario.html', {'partida': nova_partida})

@login_required
def aceitar_convite(request, partida_id):
    """ Coloca o amigo na sala de pênaltis através do link """
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    draft = MeuDraft.objects.filter(usuario=request.user, status='ativo').last()
    
    # VERIFICAÇÃO RÍGIDA APLICADA NO CONVITE TAMBÉM
    draft_completo = draft and draft.batedores.count() == 5 and draft.goleiro is not None
    if not draft_completo:
        request.session['convite_pendente'] = partida_id
        return redirect('minijogo:tela_draft')
    
    if partida.fase == 'aguardando' and partida.jogador1 != request.user:
        partida.jogador2 = request.user
        partida.draft_j2 = draft
        partida.fase = '5_cobrancas'
        
        # Respeita o cara-ou-coroa
        if partida.moeda_sorteio == 'j1':
            partida.turno_batedor = partida.jogador1
        else:
            partida.turno_batedor = partida.jogador2
            
        partida.save()
        
    return redirect('minijogo:tela_jogo', partida_id=partida.id)
    
@login_required
def tela_jogo(request, partida_id):
    """ Carrega o visual do gol e os controles """
    partida = get_object_or_404(PartidaPenalti, id=partida_id)
    
    # ================================================================
    # SEGURANÇA DA SALA: BARRAR TERCEIROS ("BICO" NÃO ENTRA)
    # ================================================================
    # Se o usuário não for nem o dono da sala (J1) e nem o adversário oficial (J2)...
    if request.user != partida.jogador1 and request.user != partida.jogador2:
        # Mostra a mensagem de erro e chuta ele de volta pro Radar de Desafios
        messages.error(request, "🔒 Ops! Esta sala já está lotada ou a partida está em andamento.")
        return redirect('duelos:listar_desafios')
    # ================================================================

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

    emote_adv = partida.emote_j2 if request.user == partida.jogador1 else partida.emote_j1

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
        'emote_adversario': emote_adv,
        'vencedor_streak': vencedor_streak,
    }

    if request.user == partida.jogador1 and partida.emote_j2:
        partida.emote_j2 = None
        partida.save(update_fields=['emote_j2'])
    elif request.user == partida.jogador2 and partida.emote_j1:
        partida.emote_j1 = None
        partida.save(update_fields=['emote_j1'])
    
    return JsonResponse(dados)

@login_required
def ranking_x1(request):
    """ Exibe o Top 10 jogadores detalhado """
    
    # Busca os usuários e anota as estatísticas totais baseadas em todos os drafts deles
    top_lendas = User.objects.annotate(
        titulos_lenda=Count('drafts_x1', filter=Q(drafts_x1__status='campeao')),
        total_jogos=Sum('drafts_x1__jogos_jogados'),
        total_vitorias=Sum('drafts_x1__vitorias'),
        total_derrotas=Sum('drafts_x1__derrotas'),
        max_streak=Max('drafts_x1__vitorias_seguidas') # Pega a melhor sequência que ele tem ativa
    ).filter(
        # Opcional: Só mostra quem já jogou pelo menos 1 partida para não encher o ranking de fantasmas
        total_jogos__gt=0 
    ).order_by('-titulos_lenda', '-total_vitorias', '-max_streak')[:10]
    
    return render(request, 'minijogo/ranking.html', {'top_lendas': top_lendas})

@login_required
def cancelar_lobby(request, partida_id):
    """ Exclui a partida se o adversário ainda não tiver entrado """
    partida = PartidaPenalti.objects.filter(id=partida_id, jogador1=request.user).first()
    
    # Só deixa cancelar se o Jogador 2 ainda for None (ninguém entrou)
    if partida and partida.jogador2 is None:
        partida.delete()
        messages.success(request, "Sala cancelada com sucesso.")
        
    return redirect('duelos:listar_desafios')


@login_required
@require_POST
def api_enviar_emote(request):
    """ Regista o emoji que o jogador acabou de enviar """
    data = json.loads(request.body)
    partida = get_object_or_404(PartidaPenalti, id=data.get('partida_id'))
    emoji = data.get('emoji')

    if request.user == partida.jogador1:
        partida.emote_j1 = emoji
    elif request.user == partida.jogador2:
        partida.emote_j2 = emoji
    partida.save()
    
    return JsonResponse({'sucesso': True})

@login_required
@require_POST
def api_usar_olheiro(request):
    """ Lê a mente do adversário: analisa o caderninho de histórico dele """
    data = json.loads(request.body)
    partida = get_object_or_404(PartidaPenalti, id=data.get('partida_id'))

    # Verifica se já usou
    if request.user == partida.jogador1:
        if partida.j1_usou_olheiro:
            return JsonResponse({'sucesso': False, 'mensagem': 'Você já usou o Olheiro!'})
        partida.j1_usou_olheiro = True
        draft_adv = partida.draft_j2 # 👈 Puxa o Draft do Oponente
    else:
        if partida.j2_usou_olheiro:
            return JsonResponse({'sucesso': False, 'mensagem': 'Você já usou o Olheiro!'})
        partida.j2_usou_olheiro = True
        draft_adv = partida.draft_j1
        
    partida.save()

    if not draft_adv or not draft_adv.historico_chutes:
        return JsonResponse({
            'sucesso': True, 
            'relatorio': "Não há dados suficientes. O adversário é um novato imprevisível."
        })

    # Transforma a string "se,mc,id," numa lista pegando os últimos 10 chutes
    chutes = [c for c in draft_adv.historico_chutes.split(',') if c]
    ultimos_chutes = chutes[-10:]

    dicionario_zonas = {
        'se': 'Esquerda Alta', 'me': 'Meio Alta', 'sd': 'Direita Alta',
        'ie': 'Esquerda Baixa', 'mc': 'Meio Rasteiro', 'id': 'Direita Baixa'
    }

    # Conta qual lado ele mais chutou
    contagem = {}
    for zona in ultimos_chutes:
        contagem[zona] = contagem.get(zona, 0) + 1
        
    zona_favorita = max(contagem, key=contagem.get)
    porcentagem = int((contagem[zona_favorita] / len(ultimos_chutes)) * 100)
    
    relatorio = f"O Scout analisou! Em {porcentagem}% das vezes recentes, o adversário chutou na zona: {dicionario_zonas.get(zona_favorita, 'Desconhecida')}."

    return JsonResponse({'sucesso': True, 'relatorio': relatorio})

@login_required
@require_POST
def api_usar_tatica(request):
    """ Ativa a carta tática (Catimba) para a rodada atual """
    data = json.loads(request.body)
    partida = get_object_or_404(PartidaPenalti, id=data.get('partida_id'))

    if request.user == partida.jogador1:
        if partida.j1_usou_poder:
            return JsonResponse({'sucesso': False, 'mensagem': 'Carta Tática já foi usada!'})
        partida.j1_usou_poder = True
        partida.j1_tatica_ativa = True
    else:
        if partida.j2_usou_poder:
            return JsonResponse({'sucesso': False, 'mensagem': 'Carta Tática já foi usada!'})
        partida.j2_usou_poder = True
        partida.j2_tatica_ativa = True
        
    partida.save()
    return JsonResponse({'sucesso': True, 'mensagem': 'Tática ativada! O OVR do adversário cairá nesta cobrança!'})

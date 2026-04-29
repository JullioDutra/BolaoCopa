import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse

from .models import (
    PartidaDuelo, 
    CategoriaDesafio, 
    ItemDesafio, 
    JogadorBanco, 
    Campeonato, 
    InscricaoCampeonato, 
    ConfrontoCampeonato
)

# ==========================================
# ARENA X1 E LOBBY PRINCIPAL
# ==========================================
def listar_desafios(request):
    # Busca todos os campeonatos para que o Radar mostre tanto os de Inscrição quanto os em Andamento (Ver Chaves)
    campeonatos = Campeonato.objects.all().order_by('-criado_em')
    
    context = {
        'campeonatos_abertos': campeonatos, # Mantido este nome para não quebrar o seu HTML
    }
    return render(request, 'duelos/listar_desafios.html', context)


@login_required
def criar_duelo(request, tipo_jogo):
    """Cria a sala sorteando um desafio aleatório do tipo escolhido."""
    # Filtra categorias pelo tipo (elenco ou trajetoria)
    categorias_disponiveis = list(CategoriaDesafio.objects.filter(tipo=tipo_jogo))
    
    if not categorias_disponiveis:
        messages.error(request, f"Nenhum desafio de {tipo_jogo} cadastrado.")
        return redirect('duelos:listar_desafios')
    
    # Sorteio aleatório da categoria
    categoria_sorteada = random.choice(categorias_disponiveis)
    
    partida = PartidaDuelo.objects.create(
        categoria=categoria_sorteada,
        jogador_criador=request.user,
        turno_de=request.user, 
        status='aguardando'
    )
    
    return redirect('duelos:lobby_espera', partida_id=partida.id)

@login_required
def lobby_espera(request, partida_id):
    """Lobby de espera com link de convite."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    
    if request.user != partida.jogador_criador:
        messages.error(request, "Acesso negado.")
        return redirect('dashboard')
        
    link_convite = request.build_absolute_uri(f"/duelos/entrar/{partida.id}/")
    
    return render(request, 'duelos/lobby.html', {
        'partida': partida,
        'link_convite': link_convite
    })

@login_required
def entrar_duelo_link(request, partida_id):
    """Entrada do convidado via link."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    
    if request.user == partida.jogador_criador:
        if partida.status == 'andamento':
            return redirect('duelos:tela_jogo', partida_id=partida.id)
        return redirect('duelos:lobby_espera', partida_id=partida.id)
        
    if partida.status != 'aguardando':
        messages.error(request, "Partida indisponível.")
        return redirect('dashboard')
        
    partida.jogador_convidado = request.user
    partida.status = 'andamento'
    partida.turno_iniciado_em = timezone.now() # Inicia o timer do primeiro turno
    partida.save()
    
    return redirect('duelos:tela_jogo', partida_id=partida.id)

def checar_oponente_api(request, partida_id):
    """Polling para o lobby detectar a entrada do oponente."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    return JsonResponse({
        'status': partida.status,
        'comecou': partida.status == 'andamento'
    })

@login_required
def tela_jogo(request, partida_id):
    """Direciona para o template específico ocultando detalhes do desafio."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    
    if request.user not in [partida.jogador_criador, partida.jogador_convidado]:
        return redirect('dashboard')

    # Busca todos os jogadores do banco para o AUTOCOMPLETE HTML5
    banco_jogadores = JogadorBanco.objects.all().order_by('nome')

    # Seleção de template baseada no tipo de jogo
    template = 'duelos/jogo_elenco.html' if partida.categoria.tipo == 'elenco' else 'duelos/jogo_trajetoria.html'
    return render(request, template, {'partida': partida, 'banco_jogadores': banco_jogadores})


def status_partida_api(request, partida_id):
    """Heartbeat do jogo: gere o tempo e os turnos (agora com 30 segundos)."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    agora = timezone.now()
    tempo_passado = 0
    
    if partida.status == 'andamento':
        tempo_passado = (agora - partida.turno_iniciado_em).total_seconds()
        
        # Gestão do tempo esgotado (ALTERADO PARA 30 SEGUNDOS)
        if tempo_passado >= 30:
            # Troca de turno automática
            partida.turno_de = partida.jogador_convidado if partida.turno_de == partida.jogador_criador else partida.jogador_criador
            partida.turno_iniciado_em = agora
            partida.erros_acumulados += 1
            partida.save()
            tempo_passado = 0

    # Calcula o tempo restante baseado nos 30 segundos
    tempo_restante = max(0, 30 - int(tempo_passado))

    return JsonResponse({
        'status': partida.status,
        'turno_atual_id': partida.turno_de.id if partida.turno_de else None,
        'tempo_restante': tempo_restante,
        'pontos_j1': partida.pontos_criador,
        'pontos_j2': partida.pontos_convidado,
        'erros_acumulados': partida.erros_acumulados,
        'revelados_ids': list(partida.itens_revelados.values_list('id', flat=True))
    })

@login_required
def enviar_palpite_api(request, partida_id):
    """Valida o palpite e processa a lógica de pontuação e encerramento."""
    if request.method == 'POST':
        partida = get_object_or_404(PartidaDuelo, id=partida_id)
        
        if request.user != partida.turno_de or partida.status != 'andamento':
            return JsonResponse({'sucesso': False, 'erro': 'Não é o seu turno.'})
            
        data = json.loads(request.body)
        chute = data.get('palpite', '').strip().lower()
        acertou = False
        
        # --- Lógica Modo Elenco ---
        if partida.categoria.tipo == 'elenco':
            itens_restantes = partida.categoria.itens.exclude(id__in=partida.itens_revelados.all())
            for item in itens_restantes:
                # USA A INTELIGÊNCIA NOVA PARA PEGAR O NOME (Banco ou Manual)
                if chute == item.get_nome().strip().lower():
                    acertou = True
                    partida.itens_revelados.add(item)
                    if request.user == partida.jogador_criador:
                        partida.pontos_criador += 1
                    else:
                        partida.pontos_convidado += 1
                    
                    if not partida.categoria.itens.exclude(id__in=partida.itens_revelados.all()).exists():
                        partida.status = 'finalizado'
                    break
        
        # --- Lógica Modo Trajetória ---
        elif partida.categoria.tipo == 'trajetoria':
            if chute == partida.categoria.resposta_oculta.strip().lower():
                acertou = True
                partida.status = 'finalizado'
                if request.user == partida.jogador_criador:
                    partida.pontos_criador += 10
                else:
                    partida.pontos_convidado += 10
        
        if not acertou:
            partida.erros_acumulados += 1
            
        if partida.status == 'andamento':
            partida.turno_de = partida.jogador_convidado if partida.turno_de == partida.jogador_criador else partida.jogador_criador
            partida.turno_iniciado_em = timezone.now()
        else:
            if partida.pontos_criador > partida.pontos_convidado:
                partida.vencedor = partida.jogador_criador
            elif partida.pontos_convidado > partida.pontos_criador:
                partida.vencedor = partida.jogador_convidado
            
        partida.save()

        # ==============================================================
        # 👇 LÓGICA DE AVANÇO DO CAMPEONATO AQUI 👇
        # ==============================================================
        if partida.status == 'finalizado' and hasattr(partida, 'confrontocampeonato'):
            vencedor_chave = partida.vencedor
            
            # Se deu empate no mata-mata, temos que passar alguém. (Aqui o criador avança como 'vantagem do empate')
            if not vencedor_chave:
                vencedor_chave = partida.jogador_criador 
                
            processar_avanco_fase(partida.confrontocampeonato, vencedor_chave)
        # ==============================================================

        return JsonResponse({'sucesso': True, 'acertou': acertou})
        
    return JsonResponse({'sucesso': False}, status=400)

@login_required
def desistir_partida_api(request, partida_id):
    """Permite a um jogador desistir, dando a vitória ao oponente."""
    if request.method == 'POST':
        partida = get_object_or_404(PartidaDuelo, id=partida_id)
        
        # Confirma que é um dos jogadores e que o jogo está a decorrer
        if request.user in [partida.jogador_criador, partida.jogador_convidado] and partida.status == 'andamento':
            partida.status = 'finalizado'
            
            # O vencedor é o outro jogador
            if request.user == partida.jogador_criador:
                partida.vencedor = partida.jogador_convidado
            else:
                partida.vencedor = partida.jogador_criador
                
            partida.save()

            # ==============================================================
            # 👇 LÓGICA DE AVANÇO DO CAMPEONATO AQUI 👇
            # ==============================================================
            if hasattr(partida, 'confrontocampeonato'):
                processar_avanco_fase(partida.confrontocampeonato, partida.vencedor)
            # ==============================================================

            return JsonResponse({'sucesso': True})
            
    return JsonResponse({'sucesso': False}, status=400)


@login_required
def historico_duelos(request):
    """Lista todas as partidas finalizadas do utilizador atual."""
    # Busca partidas onde o utilizador é criador OU convidado, e que já terminaram
    partidas = PartidaDuelo.objects.filter(
        Q(jogador_criador=request.user) | Q(jogador_convidado=request.user),
        status='finalizado'
    ).order_by('-data_criacao') # Mais recentes primeiro
    
    return render(request, 'duelos/historico.html', {'partidas': partidas})


# ==========================================
# MODO CAMPEONATO - INSCRIÇÃO E GESTÃO
# ==========================================
@login_required
def entrar_campeonato(request, codigo_convite):
    """Link público para jogadores se inscreverem no campeonato."""
    campeonato = get_object_or_404(Campeonato, codigo_convite=codigo_convite)

    # O VAR checa se a janela de transferências fechou
    if not campeonato.inscricoes_abertas():
        messages.error(request, "As inscrições para este campeonato já estão encerradas!")
        return redirect('dashboard')

    # Confirma a inscrição do jogador
    inscricao, created = InscricaoCampeonato.objects.get_or_create(
        campeonato=campeonato,
        jogador=request.user
    )

    if created:
        messages.success(request, f"Você está inscrito no {campeonato.nome}! Aguarde o sorteio das chaves.")
    else:
        messages.info(request, "Você já está inscrito neste campeonato, craque. Só aguardar!")

    return redirect('duelos:listar_desafios')

@login_required
def criar_campeonato(request):
    """Página para o Admin criar um novo Campeonato."""
    if request.method == 'POST':
        nome = request.POST.get('nome')
        dias_abertos = int(request.POST.get('dias', 1))
        
        # Calcula a data limite somando os dias escolhidos
        data_limite = timezone.now() + timezone.timedelta(days=dias_abertos)
        
        campeonato = Campeonato.objects.create(
            nome=nome,
            admin=request.user,
            data_limite_inscricao=data_limite
        )
        
        # Inscreve o próprio criador automaticamente pra já ter 1 na lista
        InscricaoCampeonato.objects.create(campeonato=campeonato, jogador=request.user)
        
        messages.success(request, f"Taça {nome} criada! Espalhe o link para a galera.")
        return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)
        
    return render(request, 'duelos/criar_campeonato.html')

@login_required
def painel_campeonato(request, campeonato_id):
    """Painel Exclusivo do Admin do Torneio (Mesclado e Otimizado)."""
    # Garante que apenas o criador (admin) acessa este painel
    campeonato = get_object_or_404(Campeonato, id=campeonato_id, admin=request.user)
    
    # Lista de inscritos
    inscritos = InscricaoCampeonato.objects.filter(campeonato=campeonato).select_related('jogador').order_by('data_inscricao')
    total_inscritos = inscritos.count()
    
    # Gerar o link de convite absoluto
    link_convite = request.build_absolute_uri(
        reverse('duelos:entrar_campeonato', kwargs={'codigo_convite': campeonato.codigo_convite})
    )
    
    context = {
        'campeonato': campeonato,
        'inscritos': inscritos,
        'link_convite': link_convite,
        'total_inscritos': total_inscritos,
        'is_admin': True,
        'faltam_jogadores': total_inscritos < 3
    }
    return render(request, 'duelos/painel_campeonato.html', context)


# ==========================================
# MODO CAMPEONATO - CHAVEAMENTO E JOGABILIDADE
# ==========================================
@login_required
def gerar_chaveamento(request, campeonato_id):
    """Sorteia e cria a tabela de chaves de mata-mata."""
    campeonato = get_object_or_404(Campeonato, id=campeonato_id, admin=request.user)

    if campeonato.status != 'inscricoes':
        messages.error(request, "As chaves já foram geradas ou o torneio já acabou.")
        return redirect('dashboard')

    # Pega todo mundo que assinou a súmula e embaralha (Sorteio cego)
    inscricoes = list(campeonato.inscritos.all())
    random.shuffle(inscricoes)
    jogadores = [inscricao.jogador for inscricao in inscricoes]
    num_jogadores = len(jogadores)

    if num_jogadores < 3:
        messages.error(request, "Falta quórum! Precisa de pelo menos 3 jogadores para dar jogo.")
        return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)

    # Lógica de chaves (4 ou 8 vagas). Se tiver 5 a 8 pessoas, usamos a chave de Quartas de Final (8 vagas).
    if num_jogadores <= 4:
        fase_inicial = 'semi'
        vagas = 4
    else:
        fase_inicial = 'quartas'
        vagas = 8

    # Se tivermos um número "quebrado" (ex: 7 jogadores pra 8 vagas), o algoritmo preenche com "None"
    # Quem cair contra "None" avança de fase de graça (W.O. automático / Bye)
    while len(jogadores) < vagas:
        jogadores.append(None)

    # Pegamos todos os desafios para sortear
    categorias_disponiveis = list(CategoriaDesafio.objects.all())

    # Monta os confrontos de 2 em 2
    ordem = 1
    for i in range(0, vagas, 2):
        j1 = jogadores[i]
        j2 = jogadores[i+1]

        # Sorteia se vai ser Elenco ou Trajetória, e qual específico
        desafio = random.choice(categorias_disponiveis) if categorias_disponiveis else None

        confronto = ConfrontoCampeonato.objects.create(
            campeonato=campeonato,
            fase=fase_inicial,
            jogador1=j1,
            jogador2=j2,
            desafio_sorteado=desafio,
            ordem_chave=ordem
        )

        # Regra do W.O. (se um jogador foi sorteado contra "Ninguém", ele avança)
        if j1 and not j2:
            confronto.status = 'wo'
            confronto.vencedor = j1
            confronto.save()
        elif j2 and not j1:
            confronto.status = 'wo'
            confronto.vencedor = j2
            confronto.save()

        ordem += 1

    # Atualiza o status do campeonato
    campeonato.status = 'andamento'
    campeonato.save()

    messages.success(request, "Sorteio realizado com sucesso! O chaveamento está pronto.")
    return redirect('duelos:ver_chaveamento', campeonato_id=campeonato.id)

@login_required
def ver_chaveamento(request, campeonato_id):
    """Página pública para os jogadores verem a tabela de jogos."""
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    
    # Se ainda tá em inscrições, não tem chave pra mostrar
    if campeonato.status == 'inscricoes':
        if campeonato.admin == request.user:
            return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)
        else:
            messages.info(request, "As chaves ainda não foram geradas pelo administrador.")
            return redirect('duelos:listar_desafios')
        
    confrontos = campeonato.confrontos.all().order_by('ordem_chave')
    
    # Separando os jogos por fase
    fases = {
        'quartas': confrontos.filter(fase='quartas'),
        'semi': confrontos.filter(fase='semi'),
        'final': confrontos.filter(fase='final')
    }
    
    context = {
        'campeonato': campeonato,
        'confrontos': confrontos, # Enviando também todos caso queira iterar de forma simples no HTML
        'fases': fases,
    }
    return render(request, 'duelos/ver_chaveamento.html', context)

@login_required
@login_required
def lobby_espera(request, partida_id):
    """Lobby de espera com link de convite."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    
    if request.user != partida.jogador_criador:
        messages.error(request, "Acesso negado.")
        return redirect('dashboard')
        
    link_convite = request.build_absolute_uri(f"/duelos/entrar/{partida.id}/")
    
    # Verifica se a partida faz parte de uma chave de campeonato
    eh_campeonato = hasattr(partida, 'confrontocampeonato')
    
    return render(request, 'duelos/lobby.html', {
        'partida': partida,
        'link_convite': link_convite,
        'eh_campeonato': eh_campeonato
    })


@login_required
def iniciar_jogo_campeonato(request, confronto_id):
    """Entrada da sala de jogo específica de uma chave do campeonato."""
    confronto = get_object_or_404(ConfrontoCampeonato, id=confronto_id)
    
    # Bloqueia se o jogo já acabou ou foi W.O.
    if confronto.status in ['finalizado', 'wo']:
        messages.warning(request, "Este confronto já está decidido!")
        return redirect('duelos:ver_chaveamento', campeonato_id=confronto.campeonato.id)

    # 1. Se a partida ainda NÃO EXISTE, o PRIMEIRO jogador a clicar cria a sala e fica aguardando
    if not confronto.partida_vinculada:
        # Quem clicou vira o "criador" (host) da sala
        j_criador = request.user
        j_convidado = confronto.jogador2 if request.user == confronto.jogador1 else confronto.jogador1

        partida = PartidaDuelo.objects.create(
            categoria=confronto.desafio_sorteado,
            jogador_criador=j_criador,
            jogador_convidado=j_convidado,
            turno_de=confronto.jogador1, # O jogador 1 da chave sempre tem a vantagem do primeiro palpite
            status='aguardando' # <-- O CRONÔMETRO AINDA NÃO RODA
        )
        confronto.partida_vinculada = partida
        confronto.status = 'andamento'
        confronto.save()
        
        # Como ele foi o primeiro a chegar, vai pro vestiário (Lobby) esperar o outro
        return redirect('duelos:lobby_espera', partida_id=partida.id)
        
    # 2. Se a partida JÁ EXISTE, significa que alguém já está lá esperando
    else:
        partida = confronto.partida_vinculada
        
        # Se a partida está aguardando e quem clicou FOI O ADVERSÁRIO (O segundo a chegar)
        if partida.status == 'aguardando' and request.user != partida.jogador_criador:
            # Apita o árbitro! O segundo chegou, a bola rola agora.
            partida.status = 'andamento'
            partida.turno_iniciado_em = timezone.now()
            partida.save()
            return redirect('duelos:tela_jogo', partida_id=partida.id)
            
        # Se a partida está aguardando mas quem clicou foi o mesmo cara que criou (voltou na tela)
        elif partida.status == 'aguardando' and request.user == partida.jogador_criador:
            return redirect('duelos:lobby_espera', partida_id=partida.id)
            
        # Se a partida já está em andamento ou finalizada
        else:
            return redirect('duelos:tela_jogo', partida_id=partida.id)

# ------------------- LÓGICA DE RESETAR O CAMPEONATO -------------------
@login_required
def resetar_campeonato(request, campeonato_id):
    """Apaga a tabela gerada e volta o campeonato para a fase de inscrições."""
    campeonato = get_object_or_404(Campeonato, id=campeonato_id, admin=request.user)
    
    # O VAR apaga todas as chaves geradas
    ConfrontoCampeonato.objects.filter(campeonato=campeonato).delete()
    
    # Volta o status do campeonato para 'inscricoes'
    campeonato.status = 'inscricoes'
    campeonato.save()
    
    messages.success(request, "Campeonato reiniciado! As chaves foram apagadas e o torneio voltou para a fase de inscrições.")
    return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)

def processar_avanco_fase(confronto, vencedor):
    """
    Função Helper: Sobe o vencedor na árvore do campeonato.
    Chamada automaticamente na API de enviar palpite ou desistir.
    """
    confronto.vencedor = vencedor
    confronto.status = 'finalizado'
    confronto.save()

    # Se for a final, acaba o campeonato e entrega a taça!
    if confronto.fase == 'final':
        campeonato = confronto.campeonato
        campeonato.status = 'finalizado'
        campeonato.save()
        return

    # Matemática do chaveamento cruzado
    # Jogo 1 e Jogo 2 vão para o Jogo 1 da próxima fase. Jogo 3 e 4 vão para o Jogo 2.
    mapa_fases = {'quartas': 'semi', 'semi': 'final'}
    proxima_fase = mapa_fases.get(confronto.fase)
    proxima_ordem = ((confronto.ordem_chave - 1) // 2) + 1

    # Busca ou cria o confronto da próxima fase
    prox_confronto, created = ConfrontoCampeonato.objects.get_or_create(
        campeonato=confronto.campeonato,
        fase=proxima_fase,
        ordem_chave=proxima_ordem
    )

    # Se a ordem do confronto atual for ímpar, ele entra como jogador 1. Se for par, jogador 2.
    if confronto.ordem_chave % 2 != 0:
        prox_confronto.jogador1 = vencedor
    else:
        prox_confronto.jogador2 = vencedor
        
    prox_confronto.save()

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CategoriaDesafio, PartidaDuelo, ItemDesafio
import json
import random
from django.utils import timezone
from django.db.models import Q

@login_required
def listar_desafios(request):
    """Tela inicial para escolha do modo de jogo."""
    return render(request, 'duelos/listar_desafios.html')

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

    # Seleção de template baseada no tipo de jogo
    template = 'duelos/jogo_elenco.html' if partida.categoria.tipo == 'elenco' else 'duelos/jogo_trajetoria.html'
    return render(request, template, {'partida': partida})

def status_partida_api(request, partida_id):
    """Heartbeat do jogo: gere o tempo e os turnos."""
    partida = get_object_or_404(PartidaDuelo, id=partida_id)
    agora = timezone.now()
    tempo_passado = 0
    
    if partida.status == 'andamento':
        tempo_passado = (agora - partida.turno_iniciado_em).total_seconds()
        
        # Gestão do tempo esgotado (15 segundos por turno)
        if tempo_passado >= 30:
            # Troca de turno automática
            partida.turno_de = partida.jogador_convidado if partida.turno_de == partida.jogador_criador else partida.jogador_criador
            partida.turno_iniciado_em = agora
            partida.erros_acumulados += 1
            partida.save()
            tempo_passado = 0

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
                if chute == item.nome.strip().lower():
                    acertou = True
                    partida.itens_revelados.add(item)
                    if request.user == partida.jogador_criador:
                        partida.pontos_criador += 1
                    else:
                        partida.pontos_convidado += 1
                    
                    # Verifica se o jogo acabou (todos os itens descobertos)
                    if not partida.categoria.itens.exclude(id__in=partida.itens_revelados.all()).exists():
                        partida.status = 'finalizado'
                    break
        
        # --- Lógica Modo Trajetória ---
        elif partida.categoria.tipo == 'trajetoria':
            # Compara com a resposta oculta da categoria
            if chute == partida.categoria.resposta_oculta.strip().lower():
                acertou = True
                partida.status = 'finalizado'
                if request.user == partida.jogador_criador:
                    partida.pontos_criador += 10
                else:
                    partida.pontos_convidado += 10
        
        if not acertou:
            partida.erros_acumulados += 1
            
        # Se o jogo continua, troca o turno e reseta o tempo
        if partida.status == 'andamento':
            partida.turno_de = partida.jogador_convidado if partida.turno_de == partida.jogador_criador else partida.jogador_criador
            partida.turno_iniciado_em = timezone.now()
        else:
            # Define o vencedor ao finalizar
            if partida.pontos_criador > partida.pontos_convidado:
                partida.vencedor = partida.jogador_criador
            elif partida.pontos_convidado > partida.pontos_criador:
                partida.vencedor = partida.jogador_convidado
            
        partida.save()
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
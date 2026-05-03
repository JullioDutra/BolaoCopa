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
    ConfrontoCampeonato,
    ClubeFutebol, 
    PerguntaClube, 
    PartidaMiniFanaticos, 
    JogadorMiniFanaticos,
    CartaTrunfo,
    PartidaTrunfo

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
# ==========================================
# MODO CAMPEONATO - CHAVEAMENTO E JOGABILIDADE
# ==========================================
@login_required
def gerar_chaveamento(request, campeonato_id):
    """Sorteia e cria a tabela distribuindo os W.O.s corretamente para evitar 'Vazio vs Vazio'."""
    campeonato = get_object_or_404(Campeonato, id=campeonato_id, admin=request.user)

    if campeonato.status != 'inscricoes':
        messages.error(request, "As chaves já foram geradas ou o torneio já acabou.")
        return redirect('dashboard')

    inscricoes = list(campeonato.inscritos.all())
    random.shuffle(inscricoes)
    jogadores = [inscricao.jogador for inscricao in inscricoes]
    num_jogadores = len(jogadores)

    if num_jogadores < 3:
        messages.error(request, "Falta quórum! Precisa de pelo menos 3 jogadores.")
        return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)

    # Define o tamanho da chave baseado no número de jogadores
    if num_jogadores <= 4:
        fase_inicial = 'semi'
        vagas = 4
    elif num_jogadores <= 8:
        fase_inicial = 'quartas'
        vagas = 8
    elif num_jogadores <= 16:
        fase_inicial = 'oitavas'
        vagas = 16
    else:
        messages.error(request, "A capacidade máxima desta versão da Copa é de 16 jogadores!")
        return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)

    categorias_disponiveis = list(CategoriaDesafio.objects.all())
    
    # ==============================================================
    # 1. NOVA LÓGICA DE DISTRIBUIÇÃO (Fim do "Vazio vs Vazio")
    # ==============================================================
    qtd_confrontos = vagas // 2
    pares = [{'j1': None, 'j2': None} for _ in range(qtd_confrontos)]
    
    # Como as vagas sempre são "a próxima potência de 2" (ex: 9 a 16 inscritos pra 16 vagas),
    # o número de inscritos SEMPRE é maior que a quantidade de confrontos iniciais (8).
    # Isso garante que a primeira passada no 'for' preenche o j1 de TODOS os jogos!
    for i, jogador in enumerate(jogadores):
        if i < qtd_confrontos:
            pares[i]['j1'] = jogador # Cabeças de chave
        else:
            pares[i - qtd_confrontos]['j2'] = jogador # Adversários
            
    # Embaralha os confrontos para os W.O.s não ficarem todos concentrados no final da tabela
    random.shuffle(pares)

    # ==============================================================
    # 2. CRIAR OS CONFRONTOS NO BANCO
    # ==============================================================
    ordem = 1
    for par in pares:
        j1 = par['j1']
        j2 = par['j2']
        desafio = random.choice(categorias_disponiveis) if categorias_disponiveis else None

        confronto = ConfrontoCampeonato.objects.create(
            campeonato=campeonato,
            fase=fase_inicial,
            jogador1=j1,
            jogador2=j2,
            desafio_sorteado=desafio,
            ordem_chave=ordem
        )

        # Regra do W.O.: Como não existe "Vazio vs Vazio", se faltar o j2, o j1 avança!
        if j1 and not j2:
            processar_avanco_fase(confronto, j1)

        ordem += 1

    # ==============================================================
    # 3. CONSTRUIR A ÁRVORE FUTURA PARA O DESIGN DA TELA
    # ==============================================================
    fases_arvore = []
    if fase_inicial == 'oitavas':
        fases_arvore = [('quartas', 4), ('semi', 2), ('final', 1)]
    elif fase_inicial == 'quartas':
        fases_arvore = [('semi', 2), ('final', 1)]
    elif fase_inicial == 'semi':
        fases_arvore = [('final', 1)]

    for nome_fase, qtd_jogos in fases_arvore:
        for i in range(1, qtd_jogos + 1):
            ConfrontoCampeonato.objects.get_or_create(
                campeonato=campeonato,
                fase=nome_fase,
                ordem_chave=i
            )

    campeonato.status = 'andamento'
    campeonato.save()

    messages.success(request, "Sorteio realizado! A tabela está montada de forma justa.")
    return redirect('duelos:ver_chaveamento', campeonato_id=campeonato.id)

@login_required
def ver_chaveamento(request, campeonato_id):
    """Página pública para os jogadores verem a árvore do torneio."""
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)
    
    if campeonato.status == 'inscricoes':
        return redirect('duelos:painel_campeonato', campeonato_id=campeonato.id)
        
    confrontos = campeonato.confrontos.all().order_by('ordem_chave')
    
    # Separando para o layout em colunas
    fases = {
        'oitavas': confrontos.filter(fase='oitavas'),
        'quartas': confrontos.filter(fase='quartas'),
        'semi': confrontos.filter(fase='semi'),
        'final': confrontos.filter(fase='final')
    }
    
    return render(request, 'duelos/ver_chaveamento.html', {'campeonato': campeonato, 'fases': fases})


def processar_avanco_fase(confronto, vencedor):
    """Sobe o vencedor na árvore do campeonato."""
    confronto.vencedor = vencedor
    confronto.status = 'finalizado'
    confronto.save()

    if confronto.fase == 'final':
        campeonato = confronto.campeonato
        campeonato.status = 'finalizado'
        campeonato.save()
        return

    # Adicionado o cruzamento das Oitavas -> Quartas
    mapa_fases = {'oitavas': 'quartas', 'quartas': 'semi', 'semi': 'final'}
    proxima_fase = mapa_fases.get(confronto.fase)
    proxima_ordem = ((confronto.ordem_chave - 1) // 2) + 1

    prox_confronto, created = ConfrontoCampeonato.objects.get_or_create(
        campeonato=confronto.campeonato,
        fase=proxima_fase,
        ordem_chave=proxima_ordem
    )

    if confronto.ordem_chave % 2 != 0:
        prox_confronto.jogador1 = vencedor
    else:
        prox_confronto.jogador2 = vencedor
        
    prox_confronto.save()

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
        
        # O VAR AVISA: Se essa chave (ex: Quartas, Semi) ainda não teve o desafio sorteado, sorteia agora!
        if not confronto.desafio_sorteado:
            categorias = list(CategoriaDesafio.objects.all())
            if categorias:
                confronto.desafio_sorteado = random.choice(categorias)
                confronto.save()
            else:
                messages.error(request, "Nenhum desafio cadastrado no sistema!")
                return redirect('duelos:ver_chaveamento', campeonato_id=confronto.campeonato.id)

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
    """Sobe o vencedor na árvore do campeonato."""
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
    # AQUI ESTAVA O ERRO: Precisamos garantir que as 'oitavas' apontam para as 'quartas'
    mapa_fases = {
        'oitavas': 'quartas', 
        'quartas': 'semi', 
        'semi': 'final'
    }
    
    proxima_fase = mapa_fases.get(confronto.fase)
    
    # Trava do VAR: Se a fase não existir no mapa, aborta pra não quebrar o banco
    if not proxima_fase:
        return

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


# ==========================================
# MODO MINI FANÁTICOS (2v2) - LOBBY E PREPARAÇÃO
# ==========================================
@login_required
def criar_mini_fanaticos(request):
    """Cria a mesa do 2v2 e já senta o criador na Dupla A."""
    partida = PartidaMiniFanaticos.objects.create(criador=request.user)
    JogadorMiniFanaticos.objects.create(partida=partida, jogador=request.user, dupla='A')
    
    return redirect('duelos:lobby_mini', partida_id=partida.id)

@login_required
def entrar_mini_fanaticos(request, partida_id):
    """Tela onde o convidado escolhe se vai jogar na Dupla A ou B."""
    partida = get_object_or_404(PartidaMiniFanaticos, id=partida_id)
    
    if partida.status != 'aguardando':
        messages.error(request, 'Esta partida já começou ou foi encerrada!')
        return redirect('dashboard')

    if JogadorMiniFanaticos.objects.filter(partida=partida, jogador=request.user).exists():
        return redirect('duelos:lobby_mini', partida_id=partida.id)

    if request.method == 'POST':
        dupla_escolhida = request.POST.get('dupla')
        if dupla_escolhida in ['A', 'B']:
            if JogadorMiniFanaticos.objects.filter(partida=partida, dupla=dupla_escolhida).count() < 2:
                JogadorMiniFanaticos.objects.create(partida=partida, jogador=request.user, dupla=dupla_escolhida)
                return redirect('duelos:lobby_mini', partida_id=partida.id)
            else:
                messages.error(request, f'A Dupla {dupla_escolhida} já está lotada!')

    # Pega quem já está nas duplas para mostrar na tela
    jogadores_a = JogadorMiniFanaticos.objects.filter(partida=partida, dupla='A')
    jogadores_b = JogadorMiniFanaticos.objects.filter(partida=partida, dupla='B')
    
    vagas_a = 2 - jogadores_a.count()
    vagas_b = 2 - jogadores_b.count()

    return render(request, 'duelos/entrar_mini.html', {
        'partida': partida, 
        'jogadores_a': jogadores_a,  # <--- NOVA LINHA
        'jogadores_b': jogadores_b,  # <--- NOVA LINHA
        'vagas_a': vagas_a, 
        'vagas_b': vagas_b
    })

@login_required
def lobby_mini(request, partida_id):
    """O Vestiário onde a galera conversa e escolhe o Time do Coração."""
    partida = get_object_or_404(PartidaMiniFanaticos, id=partida_id)
    
    jogadores_a = partida.jogadores.filter(dupla='A')
    jogadores_b = partida.jogadores.filter(dupla='B')
    clubes = ClubeFutebol.objects.all().order_by('nome')
    
    meu_jogador = partida.jogadores.filter(jogador=request.user).first()
    
    # Se o jogador tentar acessar sem ter entrado na dupla antes
    if not meu_jogador:
        return redirect('duelos:entrar_mini_fanaticos', partida_id=partida.id)

    # Salva a escolha do time do coração da dupla
    if request.method == 'POST':
        clube_id = request.POST.get('clube_id')
        if clube_id:
            clube = get_object_or_404(ClubeFutebol, id=clube_id)
            if meu_jogador.dupla == 'A':
                partida.clube_dupla_a = clube
            else:
                partida.clube_dupla_b = clube
            partida.save()
            messages.success(request, f"Time da Dupla {meu_jogador.dupla} definido para {clube.nome}!")
            return redirect('duelos:lobby_mini', partida_id=partida.id)

    link_convite = request.build_absolute_uri(reverse('duelos:entrar_mini_fanaticos', args=[partida.id]))

    return render(request, 'duelos/lobby_mini.html', {
        'partida': partida,
        'jogadores_a': jogadores_a,
        'jogadores_b': jogadores_b,
        'clubes': clubes,
        'link_convite': link_convite,
        'meu_jogador': meu_jogador,
    })

def status_lobby_mini_api(request, partida_id):
    """O Olheiro do Ajax: Checa se já tem 4 na sala e 2 times definidos."""
    partida = get_object_or_404(PartidaMiniFanaticos, id=partida_id)
    
    total_jogadores = partida.jogadores.count()
    times_definidos = partida.clube_dupla_a is not None and partida.clube_dupla_b is not None
    pronto_para_iniciar = (total_jogadores == 4 and times_definidos)

    # Se bateu a meta, apita o início do jogo automaticamente
    if pronto_para_iniciar and partida.status == 'aguardando':
        partida.status = 'andamento'
        partida.save()

    return JsonResponse({
        'status': partida.status,
        'pronto': pronto_para_iniciar,
        'total_jogadores': total_jogadores,
        'time_a_definido': partida.clube_dupla_a.nome if partida.clube_dupla_a else False,
        'time_b_definido': partida.clube_dupla_b.nome if partida.clube_dupla_b else False,
    })




# ==========================================
# MODO MINI FANÁTICOS (2v2) - O JOGO
# ==========================================
@login_required
def tela_jogo_mini(request, partida_id):
    """Carrega o campo de jogo com as 10 perguntas."""
    partida = get_object_or_404(PartidaMiniFanaticos, id=partida_id)
    meu_jogador = get_object_or_404(JogadorMiniFanaticos, partida=partida, jogador=request.user)

    # Se o craque já acabou a prova, manda direto pro vestiário de resultados
    if meu_jogador.finalizou:
        return redirect('duelos:resultado_mini', partida_id=partida.id)

    # TÁTICA AVANÇADA: Usa o ID da partida como 'semente' para o random.
    # Isso garante que o sorteio seja aleatório, mas idêntico para os 4 jogadores!
    rng = random.Random(partida.id)
    
    perguntas_a = list(partida.clube_dupla_a.perguntas.all())
    perguntas_b = list(partida.clube_dupla_b.perguntas.all())
    
    # Sorteia 5 de cada (ou o máximo que tiver, caso o banco esteja vazio)
    selecionadas_a = rng.sample(perguntas_a, min(5, len(perguntas_a)))
    selecionadas_b = rng.sample(perguntas_b, min(5, len(perguntas_b)))
    
    todas_perguntas = selecionadas_a + selecionadas_b
    rng.shuffle(todas_perguntas) # Mistura as 10 perguntas

    # Prepara o pacote para o JavaScript (AGORA COM GABARITO PARA OS MINIGAMES)
    perguntas_json = []
    for p in todas_perguntas:
        perguntas_json.append({
            'id': p.id,
            'clube': p.clube.nome,
            'tipo': p.tipo,
            'texto': p.texto_pergunta,
            'opcao_a': p.opcao_a,
            'opcao_b': p.opcao_b,
            'opcao_c': p.opcao_c,
            'opcao_d': p.opcao_d,
            'resposta_correta': p.resposta_correta, # Necessário para a trava e anagrama!
            # Pega a URL do escudo se existir no seu model (se não tiver, manda vazio)
            'escudo_url': p.clube.escudo.url if hasattr(p.clube, 'escudo') and p.clube.escudo else ''
        })

    return render(request, 'duelos/jogo_mini.html', {
        'partida': partida,
        'perguntas_json': json.dumps(perguntas_json)
    })
@login_required
def submeter_respostas_mini(request, partida_id):
    """O VAR corrige a prova, soma os pontos e trava o relógio do jogador."""
    if request.method == 'POST':
        partida = get_object_or_404(PartidaMiniFanaticos, id=partida_id)
        meu_jogador = get_object_or_404(JogadorMiniFanaticos, partida=partida, jogador=request.user)
        
        if meu_jogador.finalizou:
            return JsonResponse({'sucesso': False, 'erro': 'Você já entregou a prova!'})

        data = json.loads(request.body)
        respostas = data.get('respostas', [])
        tempo_total = data.get('tempo_total', 0.0)

        pontos = 0
        for item in respostas:
            p_id = item.get('id')
            chute = str(item.get('resposta', '')).strip().lower()
            
            try:
                pergunta = PerguntaClube.objects.get(id=p_id)
                gabarito = str(pergunta.resposta_correta).strip().lower()
                
                # Se for múltipla escolha, o JS manda 'a', 'b', 'c' ou 'd'
                # Se for aberta, manda o texto digitado
                if chute == gabarito:
                    pontos += 10
            except PerguntaClube.DoesNotExist:
                pass

        # Salva a súmula do jogador
        meu_jogador.pontos = pontos
        meu_jogador.tempo_gasto_segundos = tempo_total
        meu_jogador.finalizou = True
        meu_jogador.save()

        # Checa se todos os 4 já terminaram para decretar o fim do jogo
        if not partida.jogadores.filter(finalizou=False).exists():
            partida.status = 'finalizado'
            partida.save()

        return JsonResponse({'sucesso': True})

@login_required
def resultado_mini(request, partida_id):
    """A tela de placar final com a soma da dupla e o desempate pelo tempo."""
    partida = get_object_or_404(PartidaMiniFanaticos, id=partida_id)
    
    jogadores_a = partida.jogadores.filter(dupla='A')
    jogadores_b = partida.jogadores.filter(dupla='B')

    # Cálculos da Dupla A
    pontos_a = sum(j.pontos for j in jogadores_a)
    tempo_a = sum(j.tempo_gasto_segundos for j in jogadores_a)

    # Cálculos da Dupla B
    pontos_b = sum(j.pontos for j in jogadores_b)
    tempo_b = sum(j.tempo_gasto_segundos for j in jogadores_b)

    # O VAR do Desempate
    vencedor = None
    motivo = ""
    
    if pontos_a > pontos_b:
        vencedor = 'A'
        motivo = "Por pontos"
    elif pontos_b > pontos_a:
        vencedor = 'B'
        motivo = "Por pontos"
    else:
        # Empate em pontos? O relógio decide! (Ganha quem gastou MENOS tempo)
        if tempo_a < tempo_b:
            vencedor = 'A'
            motivo = "No tempo de desempate!"
        elif tempo_b < tempo_a:
            vencedor = 'B'
            motivo = "No tempo de desempate!"
        else:
            vencedor = 'Empate'
            motivo = "Empate absoluto!"

    context = {
        'partida': partida,
        'jogadores_a': jogadores_a,
        'jogadores_b': jogadores_b,
        'pontos_a': pontos_a,
        'tempo_a': tempo_a,
        'pontos_b': pontos_b,
        'tempo_b': tempo_b,
        'vencedor': vencedor,
        'motivo': motivo,
    }
    return render(request, 'duelos/resultado_mini.html', context)


# ==========================================
# VIEWS DO SUPER TRUNFO
# ==========================================
@login_required
def criar_trunfo(request):
    """Cria a mesa de Trunfo e define que o criador começa jogando."""
    partida = PartidaTrunfo.objects.create(
        criador=request.user,
        turno_de=request.user, # O dono da bola começa
        status='aguardando'
    )
    return redirect('duelos:lobby_trunfo', partida_id=partida.id)

@login_required
def entrar_trunfo(request, partida_id):
    """O convidado entra na mesa através do link."""
    partida = get_object_or_404(PartidaTrunfo, id=partida_id)
    
    if request.user == partida.criador:
        return redirect('duelos:lobby_trunfo', partida_id=partida.id)
        
    if partida.status == 'aguardando' and not partida.convidado:
        partida.convidado = request.user
        partida.status = 'andamento'
        
        # MODO ROUBA MONTE: Cada um começa com 5 cartas!
        partida.pontos_criador = 5
        partida.pontos_convidado = 5
        
        # Sorteia as duas primeiras cartas
        cartas = list(CartaTrunfo.objects.all())
        if len(cartas) >= 2:
            sorteadas = random.sample(cartas, 2)
            partida.carta_criador = sorteadas[0]
            partida.carta_convidado = sorteadas[1]
            
        partida.save()
        return redirect('duelos:tela_jogo_trunfo', partida_id=partida.id)
        
    return redirect('dashboard')

@login_required
def lobby_trunfo(request, partida_id):
    partida = get_object_or_404(PartidaTrunfo, id=partida_id)
    link_convite = request.build_absolute_uri(reverse('duelos:entrar_trunfo', args=[partida.id]))
    
    # Mudamos o HTML alvo aqui na linha de baixo:
    return render(request, 'duelos/lobby_trunfo.html', {
        'partida': partida,
        'link_convite': link_convite,
    })

@login_required
def tela_jogo_trunfo(request, partida_id):
    partida = get_object_or_404(PartidaTrunfo, id=partida_id)
    return render(request, 'duelos/jogo_trunfo.html', {'partida': partida})

@login_required
def status_trunfo_api(request, partida_id):
    """O Frontend fica chamando essa API para atualizar a tela."""
    partida = get_object_or_404(PartidaTrunfo, id=partida_id)
    
    # Identifica quem está pedindo o status para mandar a carta certa
    minha_carta = partida.carta_criador if request.user == partida.criador else partida.carta_convidado
    carta_adv = partida.carta_convidado if request.user == partida.criador else partida.carta_criador

    # Formata a carta para o JSON
    def formatar_carta(c):
        if not c: return None
        return {
            'nome': c.nome, 'pos': c.posicao, 'ovr': c.overall,
            'img': c.foto.url if c.foto else 'https://i.pravatar.cc/150', # Foto genérica se estiver sem
            'stats': {
                'rit': c.ritmo, 'fin': c.finalizacao, 'pas': c.passe, 
                'dri': c.drible, 'def': c.defesa, 'fis': c.fisico
            }
        }

    return JsonResponse({
        'status': partida.status,
        'rodada': partida.rodada_atual,
        'minha_vez': partida.turno_de == request.user,
        'pontos_meus': partida.pontos_criador if request.user == partida.criador else partida.pontos_convidado,
        'pontos_adv': partida.pontos_convidado if request.user == partida.criador else partida.pontos_criador,
        'minha_carta': formatar_carta(minha_carta),
        'carta_adv_info': formatar_carta(carta_adv) # Enviamos oculta pro JS só revelar na hora H
    })

@login_required
def batalhar_trunfo_api(request, partida_id):
    """A mágica do combate e do ROUBA MONTE!"""
    if request.method == 'POST':
        partida = get_object_or_404(PartidaTrunfo, id=partida_id)
        
        if partida.turno_de != request.user:
            return JsonResponse({'erro': 'Não é a sua vez!'})
            
        data = json.loads(request.body)
        atributo = data.get('atributo') 
        
        mapa_atributos = {
            'rit': 'ritmo', 'fin': 'finalizacao', 'pas': 'passe',
            'dri': 'drible', 'def': 'defesa', 'fis': 'fisico'
        }
        campo_real = mapa_atributos.get(atributo)
        
        valor_criador = getattr(partida.carta_criador, campo_real)
        valor_convidado = getattr(partida.carta_convidado, campo_real)
        
        vencedor_rodada = None
        
        # LÓGICA DO ROUBO DE CARTAS
        if valor_criador > valor_convidado:
            partida.pontos_criador += 1
            partida.pontos_convidado -= 1
            vencedor_rodada = partida.criador
        elif valor_convidado > valor_criador:
            partida.pontos_convidado += 1
            partida.pontos_criador -= 1
            vencedor_rodada = partida.convidado
            
        # Passa o turno para o perdedor da rodada (ou mantém se empatou)
        if vencedor_rodada and vencedor_rodada != partida.turno_de:
            partida.turno_de = vencedor_rodada
            
        partida.rodada_atual += 1
        
        # VERIFICA SE ALGUÉM ZEROU AS CARTAS (FIM DE JOGO)
        if partida.pontos_criador <= 0 or partida.pontos_convidado <= 0:
            partida.status = 'finalizado'
        else:
            # Só sorteia novas cartas se o jogo for continuar
            cartas = list(CartaTrunfo.objects.all())
            if len(cartas) >= 2:
                sorteadas = random.sample(cartas, 2)
                partida.carta_criador = sorteadas[0]
                partida.carta_convidado = sorteadas[1]
            
        partida.save()
        
        return JsonResponse({
            'sucesso': True,
            'vencedor_id': vencedor_rodada.id if vencedor_rodada else None,
            'valor_j1': valor_criador,
            'valor_j2': valor_convidado
        })


@login_required
def resultado_trunfo(request, partida_id):
    """Vestiário final: Exibe quem ganhou o duelo."""
    partida = get_object_or_404(PartidaTrunfo, id=partida_id)
    
    # Descobre quem é o dono das 10 cartas
    if partida.pontos_criador == 0:
        campeao = partida.convidado
    elif partida.pontos_convidado == 0:
        campeao = partida.criador
    else:
        campeao = None # Caso de erro ou empate forçado
        
    eh_campeao = request.user == campeao
        
    return render(request, 'duelos/resultado_trunfo.html', {
        'partida': partida,
        'campeao': campeao,
        'eh_campeao': eh_campeao
    })
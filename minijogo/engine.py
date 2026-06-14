import random
from .models import MeuDraft, ElencoHistorico, CartaJogador

# ==========================================
# 1. MOTOR DO DRAFT (SORTEIO E PRANCHETA)
# ==========================================
def iniciar_draft(usuario):
    """ Cria um draft novo zerado para o usuário """
    draft = MeuDraft.objects.create(usuario=usuario)
    return sortear_novo_elenco(draft)

def sortear_novo_elenco(draft):
    """ Puxa um time aleatório do banco de dados para o usuário escolher uma carta """
    todos_elencos = list(ElencoHistorico.objects.all())
    if todos_elencos:
        draft.elenco_sorteado = random.choice(todos_elencos)
        draft.save()
    return draft.elenco_sorteado

def selecionar_carta(draft, carta_id):
    """ Adiciona a carta escolhida à prancheta do jogador """
    try:
        carta = CartaJogador.objects.get(id=carta_id)
    except CartaJogador.DoesNotExist:
        return False, "Carta não encontrada!"
    
    # Verifica se já bateu o limite de cartas
    qtd_batedores = draft.batedores.count()
    
    if carta.posicao == 'goleiro':
        if draft.goleiro is None:
            draft.goleiro = carta
        else:
            return False, "Você já tem um goleiro!"
    else:
        if qtd_batedores < 5:
            draft.batedores.add(carta)
        else:
            return False, "Você já tem 5 batedores de linha!"
            
    draft.save()
    
    # Se o draft estiver completo (5 de linha + 1 goleiro), para de sortear times
    if draft.batedores.count() == 5 and draft.goleiro is not None:
        draft.elenco_sorteado = None
        draft.save()
        return True, "Draft Concluído! Pronto para jogar."
    
    # Se ainda faltam jogadores, sorteia o próximo elenco
    sortear_novo_elenco(draft)
    return True, "Carta adicionada com sucesso!"


# ==========================================
# 2. MOTOR DO X1 (CÁLCULOS E TURNOS)
# ==========================================
def processar_cobranca(partida):
    """ Chamada quando os dois jogadores escolheram seus lados """
    
    # 1. Busca as cartas usadas (Trata Timeout se a pessoa não escolheu)
    if partida.chute_zona == 'timeout':
        gol = False
    else:
        batedor = CartaJogador.objects.get(id=partida.chute_carta_id)
        goleiro = CartaJogador.objects.get(id=partida.defesa_carta_id)
        
        # 2. A Lógica Matemática (Batalha de OVR)
        if partida.chute_zona != partida.defesa_zona:
            # Goleiro pulou pro lado errado! 
            chance_erro = max(0, 100 - batedor.over) / 1.5 
            dado = random.uniform(0, 100)
            gol = False if dado < chance_erro else True
        else:
            # Goleiro pulou pro lado certo! 
            chance_batedor = (batedor.over / (batedor.over + goleiro.over)) * 100
            dado = random.uniform(0, 100)
            gol = True if dado <= chance_batedor else False

    # 3. Atualiza o Placar
    if gol:
        if partida.turno_batedor == partida.jogador1:
            partida.placar_j1 += 1
        else:
            partida.placar_j2 += 1

    # 4. Prepara a Próxima Cobrança (Vira o Turno)
    partida.chute_zona = None
    partida.chute_carta_id = None
    partida.defesa_zona = None
    partida.defesa_carta_id = None
    
    partida.chutes_na_rodada += 1
    
    # Alterna quem bate o próximo pênalti
    if partida.turno_batedor == partida.jogador1:
        partida.turno_batedor = partida.jogador2
    else:
        partida.turno_batedor = partida.jogador1

    # Se os dois já chutaram, avança a rodada
    if partida.chutes_na_rodada >= 2:
        partida.chutes_na_rodada = 0
        partida.rodada_atual += 1

    # 5. Verifica se o jogo acabou
    verificar_fim_de_jogo(partida)
    
    partida.save()


# ==========================================
# 3. REGRAS DE VITÓRIA, ELIMINAÇÃO E TAÇA
# ==========================================
def verificar_fim_de_jogo(partida):
    """ Confere a matemática para ver se o jogo vai acabar ou ir para Alternadas """
    
    # Só avalia o placar quando os DOIS jogadores terminarem de chutar na rodada
    if partida.chutes_na_rodada == 0:
        
        if partida.fase == '5_cobrancas':
            chutes_restantes = 5 - (partida.rodada_atual - 1)
            
            # Vitória matemática antecipada (Ex: 3x0 faltando 2 chutes)
            if partida.placar_j1 > partida.placar_j2 + chutes_restantes:
                encerrar_partida(partida, vencedor=partida.jogador1)
            elif partida.placar_j2 > partida.placar_j1 + chutes_restantes:
                encerrar_partida(partida, vencedor=partida.jogador2)
                
            # Acabaram os 5 chutes
            elif partida.rodada_atual > 5:
                if partida.placar_j1 == partida.placar_j2:
                    partida.fase = 'alternadas' # Empatou, vamos pra morte súbita!
                elif partida.placar_j1 > partida.placar_j2:
                    encerrar_partida(partida, vencedor=partida.jogador1)
                else:
                    encerrar_partida(partida, vencedor=partida.jogador2)

        # Morte Súbita (Alternadas)
        elif partida.fase == 'alternadas':
            if partida.placar_j1 > partida.placar_j2:
                encerrar_partida(partida, vencedor=partida.jogador1)
            elif partida.placar_j2 > partida.placar_j1:
                encerrar_partida(partida, vencedor=partida.jogador2)


def encerrar_partida(partida, vencedor):
    """ Finaliza o X1 e gerencia as 10 vitórias ou eliminação """
    partida.fase = 'finalizado'
    partida.vencedor = vencedor
    
    draft_vencedor = partida.draft_j1 if vencedor == partida.jogador1 else partida.draft_j2
    draft_perdedor = partida.draft_j2 if vencedor == partida.jogador1 else partida.draft_j1
    
    # O Perdedor dá adeus ao time
    if draft_perdedor:
        draft_perdedor.status = 'eliminado'
        draft_perdedor.save()
    
    # O Venced

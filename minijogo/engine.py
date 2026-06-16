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
    
    if draft.batedores.count() == 5 and draft.goleiro is not None:
        draft.elenco_sorteado = None
        draft.save()
        return True, "Draft Concluído! Pronto para jogar."
    
    sortear_novo_elenco(draft)
    return True, "Carta adicionada com sucesso!"


# ==========================================
# 2. A MATEMÁTICA DO PÊNALTI
# ==========================================

def calcular_resultado_penalti(chute_zona, defesa_zona, batedor_ovr, goleiro_ovr, rodada_atual, tatica_batedor_ativa=False, tatica_goleiro_ativa=False):
    """
    Motor matemático que define o resultado da cobrança baseado em RPG, zonas, pressão e táticas.
    """
    # 1. MAPEAMENTO DAS ZONAS ALTAS (A "Gaveta")
    zonas_altas = ['se', 'me', 'sd']
    chutou_no_alto = chute_zona in zonas_altas

    # =========================================================
    # CENA 1: GOLEIRO PULOU PARA O LADO ERRADO
    # =========================================================
    if chute_zona != defesa_zona:
        chance_erro = 5  
        if chutou_no_alto:
            chance_erro = 22  

        sorteio = random.randint(1, 100)
        if sorteio <= chance_erro:
            if chutou_no_alto:
                return random.choice(['isolou', 'trave'])
            else:
                return random.choice(['recuou', 'trave']) 
        return 'gol'

    # =========================================================
    # CENA 2: GOLEIRO PULOU PARA O LADO CERTO (Batalha de OVR)
    # =========================================================
    
    # RECOMPENSA DA GAVETA (+15)
    bonus_gaveta = 15 if chutou_no_alto else 0
    
    # 💥 O "BUFF" DO GOLEIRO: Se acertou o lado, ganha +15 de OVR por puro reflexo!
    bonus_acerto_lado = 15
    
    # FATOR PRESSÃO (A partir da 5ª rodada a perna treme)
    fator_sorte_max_batedor = 20
    if rodada_atual >= 5 and batedor_ovr < 88:
        fator_sorte_max_batedor = 10 # O dado do batedor cai pela metade!

    # APLICA A CARTA TÁTICA (CATIMBA)
    if tatica_goleiro_ativa:
        batedor_ovr = int(batedor_ovr / 2)
    if tatica_batedor_ativa:
        goleiro_ovr = int(goleiro_ovr / 2)

    # Rolando os dados com as novas vantagens
    poder_batedor = batedor_ovr + bonus_gaveta + random.randint(1, fator_sorte_max_batedor)
    poder_goleiro = goleiro_ovr + bonus_acerto_lado + random.randint(1, 20)

    # Quem ganha a disputa?
    if poder_batedor > poder_goleiro:
        if poder_batedor - poder_goleiro <= 3:
            return 'frango' 
        return 'gol'
    else:
        return 'defendeu'


# ==========================================
# 3. MOTOR DO X1 (CALCULA A RODADA E VIRA O TURNO)
# ==========================================
def processar_cobranca(partida):
    """ Chamada quando os dois jogadores escolheram seus lados """
    
    if partida.chute_zona == 'timeout':
        gol = False
        resultado_lance = 'isolou'
    else:
        batedor = CartaJogador.objects.get(id=partida.chute_carta_id)
        goleiro = CartaJogador.objects.get(id=partida.defesa_carta_id)
        
        # Descobre quem é o batedor e quem é o goleiro para aplicar as táticas
        tatica_batedor_ativa = False
        tatica_goleiro_ativa = False
        
        if partida.turno_batedor == partida.jogador1:
            tatica_batedor_ativa = partida.j1_tatica_ativa
            tatica_goleiro_ativa = partida.j2_tatica_ativa
        else:
            tatica_batedor_ativa = partida.j2_tatica_ativa
            tatica_goleiro_ativa = partida.j1_tatica_ativa
        
        # Passando as variáveis na ordem certa para a função
        resultado_lance = calcular_resultado_penalti(
            chute_zona=partida.chute_zona, 
            defesa_zona=partida.defesa_zona, 
            batedor_ovr=batedor.over, 
            goleiro_ovr=goleiro.over, 
            rodada_atual=partida.rodada_atual,
            tatica_batedor_ativa=tatica_batedor_ativa,
            tatica_goleiro_ativa=tatica_goleiro_ativa
        )
        
        gol = True if resultado_lance in ['gol', 'frango'] else False

    # Atualiza o Placar
    if gol:
        if partida.turno_batedor == partida.jogador1:
            partida.placar_j1 += 1
        else:
            partida.placar_j2 += 1

    # --- SALVA O REPLAY PARA A TELA ---
    partida.ultimo_chute_zona = partida.chute_zona
    partida.ultima_defesa_zona = partida.defesa_zona
    partida.ultimo_resultado = resultado_lance

    # 💥 NOVIDADE: Salva a zona chutada no perfil do batedor para o Olheiro
    if partida.chute_zona and partida.chute_zona != 'timeout':
        draft_batedor = partida.draft_j1 if partida.turno_batedor == partida.jogador1 else partida.draft_j2
        if draft_batedor:
            draft_batedor.historico_chutes += f"{partida.chute_zona}," # Grava separando por vírgula
            draft_batedor.save()

    # Prepara a Próxima Cobrança (Limpa as escolhas atuais e os poderes)
    partida.chute_zona = None
    partida.chute_carta_id = None
    partida.defesa_zona = None
    partida.defesa_carta_id = None
    
    # RESETA OS PODERES TÁTICOS PARA A PRÓXIMA RODADA
    partida.j1_tatica_ativa = False
    partida.j2_tatica_ativa = False
    
    partida.chutes_na_rodada += 1
    
    # Alterna quem bate
    if partida.turno_batedor == partida.jogador1:
        partida.turno_batedor = partida.jogador2
    else:
        partida.turno_batedor = partida.jogador1

    if partida.chutes_na_rodada >= 2:
        partida.chutes_na_rodada = 0
        partida.rodada_atual += 1

    verificar_fim_de_jogo(partida)
    partida.save()


# ==========================================
# 4. REGRAS DE VITÓRIA, ELIMINAÇÃO E TAÇA
# ==========================================
def verificar_fim_de_jogo(partida):
    """ Confere a matemática para ver se o jogo vai acabar ou ir para Alternadas """
    
    if partida.chutes_na_rodada == 0:
        if partida.fase == '5_cobrancas':
            chutes_restantes = 5 - (partida.rodada_atual - 1)
            
            # Vitória matemática antecipada (Ex: 3x0 faltando 2 chutes)
            if partida.placar_j1 > partida.placar_j2 + chutes_restantes:
                encerrar_partida(partida, vencedor=partida.jogador1)
            elif partida.placar_j2 > partida.placar_j1 + chutes_restantes:
                encerrar_partida(partida, vencedor=partida.jogador2)
                
            # Acabaram os 5 chutes e não foi resolvido antecipado
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
    """ Finaliza o X1 e atualiza TUDO para o Ranking """
    partida.fase = 'finalizado'
    partida.vencedor = vencedor
    
    # Identifica os drafts
    draft_vencedor = partida.draft_j1 if vencedor == partida.jogador1 else partida.draft_j2
    draft_perdedor = partida.draft_j2 if vencedor == partida.jogador1 else partida.draft_j1
    
    # 👈 ATUALIZA ESTATÍSTICAS DO PERDEDOR
    if draft_perdedor:
        draft_perdedor.status = 'eliminado'
        draft_perdedor.jogos_jogados += 1
        draft_perdedor.derrotas += 1
        draft_perdedor.vitorias_seguidas = 0 # Quebrou a invencibilidade
        draft_perdedor.save()
    
    # 👈 ATUALIZA ESTATÍSTICAS DO VENCEDOR
    if draft_vencedor:
        draft_vencedor.jogos_jogados += 1
        draft_vencedor.vitorias += 1
        draft_vencedor.vitorias_seguidas += 1
        
        if draft_vencedor.vitorias_seguidas >= 10:
            draft_vencedor.status = 'campeao'
            
        draft_vencedor.save()

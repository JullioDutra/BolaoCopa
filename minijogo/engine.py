import random
from .models import MeuDraft, ElencoHistorico, CartaJogador

def iniciar_draft(usuario):
    """ Cria um draft novo zerado para o usuário """
    draft = MeuDraft.objects.create(usuario=usuario)
    return sortear_novo_elenco(draft)

def sortear_novo_elenco(draft):
    """ Puxa um time aleatório do banco de dados para o usuário escolher uma carta """
    todos_elencos = list(ElencoHistorico.objects.all())
    elenco_sorteado = random.choice(todos_elencos)
    
    draft.elenco_sorteado = elenco_sorteado
    draft.save()
    return elenco_sorteado

def selecionar_carta(draft, carta_id):
    """ Adiciona a carta escolhida à prancheta do jogador """
    carta = CartaJogador.objects.get(id=carta_id)
    
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



def calcular_resultado_penalti(batedor, goleiro, alvo_chute, pulo_goleiro):
    """ Retorna o resultado final do chute ('gol', 'defesa', 'frango', 'isolou', 'trave') """
    
    # CENÁRIO A: Goleiro pulou para o lado ERRADO
    if alvo_chute != pulo_goleiro:
        # Batedor tem a faca e o queijo na mão, mas o Over define se ele treme na base
        # Fórmula de erro: Quanto menor o Over, maior a chance de isolar.
        chance_erro = max(0, 100 - batedor.over) / 1.5  # Ex: Over 85 -> 10% chance de errar
        
        dado = random.uniform(0, 100)
        if dado < chance_erro:
            return random.choice(['isolou', 'trave']) # Errou sozinho!
        else:
            return 'gol' # Golaço padrão
            
    # CENÁRIO B: Goleiro pulou para o lado CERTO (Batalha de Overs)
    else:
        # Fórmula: (Over Batedor / (Over Batedor + Over Goleiro)) * 100
        # Ex: Neymar (92) vs Cássio (85) -> (92 / 177) * 100 = 51.9% chance de passar mesmo com o goleiro indo nela
        chance_batedor = (batedor.over / (batedor.over + goleiro.over)) * 100
        
        dado = random.uniform(0, 100)
        
        if dado <= chance_batedor:
            return 'frango' # Bola passou raspando ou por baixo do goleiro (GOL)
        else:
            return 'defesa' # Goleiro foi buscar (NÃO GOL)
        

def processar_fim_de_rodada(partida):
    """ Verifica o status da partida após ambos chutarem na rodada """
    
    # Lógica Matemática para a Fase de 5 Cobranças
    if partida.fase == '5_cobrancas':
        chutes_restantes = 5 - partida.rodada_atual
        
        # Se for matematicamente impossível virar (Ex: 3x0 faltando 2 chutes)
        if partida.placar_j1 > partida.placar_j2 + chutes_restantes:
            encerrar_partida(partida, vencedor=partida.jogador1)
            
        elif partida.placar_j2 > partida.placar_j1 + chutes_restantes:
            encerrar_partida(partida, vencedor=partida.jogador2)
            
        # Se chegou na 5ª cobrança e está empatado
        elif partida.rodada_atual == 5 and partida.placar_j1 == partida.placar_j2:
            partida.fase = 'alternadas'
            partida.rodada_atual += 1
            partida.save()
            
        else:
            partida.rodada_atual += 1
            partida.save()

    # Lógica para Morte Súbita (Alternadas)
    elif partida.fase == 'alternadas':
        if partida.placar_j1 > partida.placar_j2:
            encerrar_partida(partida, vencedor=partida.jogador1)
        elif partida.placar_j2 > partida.placar_j1:
            encerrar_partida(partida, vencedor=partida.jogador2)
        else:
            # Continua empatado, vamos pra próxima alternada
            partida.rodada_atual += 1
            partida.save()


def encerrar_partida(partida, vencedor):
    """ Define o fim do X1 e aplica as regras de progressão (10 Wins ou Eliminação) """
    partida.fase = 'finalizado'
    partida.vencedor = vencedor
    partida.save()
    
    # Atualiza o perdedor
    perdedor_draft = partida.draft_j2 if vencedor == partida.jogador1 else partida.draft_j1
    perdedor_draft.status = 'eliminado'
    perdedor_draft.save()
    
    # Atualiza o vencedor
    vencedor_draft = partida.draft_j1 if vencedor == partida.jogador1 else partida.draft_j2
    vencedor_draft.vitorias_seguidas += 1
    
    if vencedor_draft.vitorias_seguidas >= 10:
        vencedor_draft.status = 'campeao'
        # Aqui você pode chamar uma função para pagar moedas na carteira dele!
        
    vencedor_draft.save()

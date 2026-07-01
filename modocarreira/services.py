import random
from django.db import transaction
from .models import Avatar, Clube, ServidorConfig, PartidaMundo, EscalacaoPosicao, ConflitoVestiario
import json
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


# Configuração da API (Coloque sua chave no settings.py ou variável de ambiente)
# genai.configure(api_key=settings.GEMINI_API_KEY)

def checar_gatilho_dilema():
    """ 30% de chance de gerar um dilema após o treino """
    return random.randint(1, 100) <= 30

def gerar_dilema_ia(avatar):
    """
    Chama a IA Generativa para criar um dilema único baseado no contexto do Avatar.
    Possui um Fallback seguro para evitar quebras no PythonAnywhere.
    """
    clube_nome = avatar.clube_atual.nome if avatar.clube_atual else "clube de várzea"
    
    prompt = f"""
    Você é o mestre de um RPG de futebol. Crie um evento aleatório (dilema) que aconteceu hoje com o jogador {avatar.nome_camisa}, que tem {avatar.idade_atual} anos e joga como {avatar.get_arquetipo_display()} no {clube_nome}.
    O evento deve ser realista, curto e focado em bastidores (imprensa, vestiário, noitada, torcida).
    
    Você DEVE retornar APENAS um JSON válido. Nenhuma palavra a mais, sem formatação markdown (```json).
    Use EXATAMENTE esta estrutura:
    {{
        "titulo": "Título Curto",
        "descricao": "A história de até 3 linhas.",
        "opcao_A": {{
            "texto": "Ação focada na mídia/fama.",
            "consequencia_tipo": "media_fama",
            "consequencia_valor": 5,
            "penalidade_tipo": "moral",
            "penalidade_valor": -5
        }},
        "opcao_B": {{
            "texto": "Ação focada no grupo/treino.",
            "consequencia_tipo": "moral",
            "consequencia_valor": 5,
            "penalidade_tipo": "media_fama",
            "penalidade_valor": -2
        }}
    }}
    """
    
    try:
        # Configura o modelo para forçar saída em JSON (O Gemini 1.5 Flash é o mais rápido e barato)
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        response = model.generate_content(prompt)
        
        # Converte a resposta em dicionário Python
        dilema_dict = json.loads(response.text)
        return dilema_dict
        
    except Exception as e:
        # PLANO B: Se a API der Timeout, limite de cota ou erro no PythonAnywhere, joga um dilema padrão.
        print(f"Erro na IA Generativa: {e}")
        return {
            "titulo": "Fofoca de Corredor",
            "descricao": f"Vazou um boato de que {avatar.nome_camisa} está forçando uma saída do {clube_nome}. A torcida está cobrando explicações nas redes sociais.",
            "opcao_A": {
                "texto": "Fazer uma live alimentando o boato.",
                "consequencia_tipo": "media_fama",
                "consequencia_valor": 5,
                "penalidade_tipo": "moral",
                "penalidade_valor": -10
            },
            "opcao_B": {
                "texto": "Beijar o escudo no próximo treino.",
                "consequencia_tipo": "moral",
                "consequencia_valor": 8,
                "penalidade_tipo": "media_fama",
                "penalidade_valor": -2
            }
        }

def resolver_dilema(avatar, opcao_escolhida_dict):
    """ Aplica os buffs e debuffs da escolha do jogador """
    attr_ganho = opcao_escolhida_dict['consequencia_tipo']
    valor_ganho = opcao_escolhida_dict['consequencia_valor']
    if hasattr(avatar, attr_ganho):
        setattr(avatar, attr_ganho, min(getattr(avatar, attr_ganho) + valor_ganho, 99))

    attr_perda = opcao_escolhida_dict['penalidade_tipo']
    valor_perda = opcao_escolhida_dict['penalidade_valor'] # Já vem negativo
    if hasattr(avatar, attr_perda):
        setattr(avatar, attr_perda, max(getattr(avatar, attr_perda) + valor_perda, 1))

    avatar.save()



def calcular_dna_inicial(arquetipo):
    """ Define os status base dependendo do estilo de jogo """
    dna = {'fisico': 60, 'tecnica': 60, 'inteligencia': 60, 'midia': 20}
    
    if arquetipo == 'xerife':
        dna.update({'fisico': 75, 'tecnica': 45, 'inteligencia': 65, 'midia': 15})
    elif arquetipo == 'maestro':
        dna.update({'fisico': 50, 'tecnica': 70, 'inteligencia': 75, 'midia': 25})
    elif arquetipo == 'matador':
        dna.update({'fisico': 65, 'tecnica': 75, 'inteligencia': 55, 'midia': 40})
    elif arquetipo == 'motorzinho':
        dna.update({'fisico': 60, 'tecnica': 65, 'inteligencia': 50, 'midia': 50})
        
    return dna

def calcular_teto_potencial():
    """ RNG para definir o potencial máximo oculto do jogador (Fator Bagre vs Craque) """
    sorte = random.randint(1, 100)
    if sorte <= 10: return random.randint(88, 94) # 10% Craque Geracional
    elif sorte <= 30: return random.randint(82, 87) # 20% Excelente Jogador
    elif sorte <= 70: return random.randint(76, 81) # 40% Jogador de Série A
    else: return random.randint(70, 75) # 30% Bagre / Operário

def sortear_clube_peneira():
    """ 70% chance Série C, 20% Série B, 10% Série A """
    sorte = random.randint(1, 100)
    if sorte <= 70: divisao = 'C'
    elif sorte <= 90: divisao = 'B'
    else: divisao = 'A'

    clubes_disponiveis = Clube.objects.filter(divisao=divisao)
    if not clubes_disponiveis.exists():
        # Fallback caso não haja times criados na divisão sorteada
        clubes_disponiveis = Clube.objects.all()
    
    if clubes_disponiveis.exists():
        return random.choice(clubes_disponiveis)
    return None

@transaction.atomic
def criar_avatar_peneira(usuario, nome_camisa, arquetipo):
    """ Serviço principal executado quando o jogador assina o contrato """
    config = ServidorConfig.objects.first()
    temporada = config.temporada_atual if config else 1
    
    dna = calcular_dna_inicial(arquetipo)
    teto = calcular_teto_potencial()
    clube_sorteado = sortear_clube_peneira()
    
    avatar = Avatar.objects.create(
        usuario=usuario,
        nome_camisa=nome_camisa,
        arquetipo=arquetipo,
        clube_atual=clube_sorteado,
        temporada_nascimento=temporada,
        teto_potencial_oculto=teto,
        fisico=dna['fisico'],
        tecnica=dna['tecnica'],
        inteligencia=dna['inteligencia'],
        media_fama=dna['midia']
    )
    
    return avatar



def processar_treino(avatar, tipo_treino):
    """
    Processa a rotina diária de treinos, consumindo Pontos de Ação (AP)
    e evoluindo os atributos do jogador, limitados ao seu Teto de Potencial.
    """
    if avatar.pontos_acao_diarios <= 0:
        raise ValueError("Você não tem Pontos de Ação (Energia) suficientes hoje.")

    # Consome a energia do dia
    avatar.pontos_acao_diarios -= 1

    # Dicionário de ganhos (Pode ser ajustado para balanceamento)
    ganhos = {
        'fisico': ('fisico', random.randint(1, 2)),
        'tecnico': ('tecnica', random.randint(1, 2)),
        'tatico': ('inteligencia', random.randint(1, 2)),
        'midia': ('media_fama', random.randint(1, 3))
    }

    if tipo_treino not in ganhos:
        raise ValueError("Tipo de treino inválido.")

    atributo, valor_ganho = ganhos[tipo_treino]
    valor_atual = getattr(avatar, atributo)

    # Verifica se a evolução do atributo base não ultrapassa o Teto Oculto
    # Exceção: Mídia (Fama) não tem teto de habilidade de campo, pode ir a 99.
    if atributo != 'media_fama' and avatar.ovr_calculado >= avatar.teto_potencial_oculto:
        # Se atingiu o teto, o treino dá apenas XP residual ou falha silenciosamente na evolução do OVR
        avatar.xp_disponivel += 10 
    else:
        # Aplica o ganho garantindo que não passe de 99
        novo_valor = min(valor_atual + valor_ganho, 99)
        setattr(avatar, atributo, novo_valor)

    avatar.save()
    
    return {
        'atributo_treinado': atributo,
        'valor_ganho': valor_ganho,
        'novo_ovr': avatar.ovr_calculado,
        'ap_restante': avatar.pontos_acao_diarios
    }




def checar_gatilho_dilema():
    """ 30% de chance de gerar um dilema após o treino """
    return random.randint(1, 100) <= 30

def gerar_dilema_ia(avatar):
    """
    Chama a IA Generativa para criar um dilema único baseado no contexto do Avatar.
    """
    clube_nome = avatar.clube_atual.nome if avatar.clube_atual else "clube de várzea"
    
    prompt = f"""
    Você é o narrador de um RPG de futebol. Crie um evento aleatório (dilema) que aconteceu hoje com o jogador {avatar.nome_camisa}, que tem {avatar.idade_atual} anos e joga como {avatar.get_arquetipo_display()} no {clube_nome}.
    
    O evento deve ser realista e divertido (ex: briga no vestiário, fofoca na mídia, proposta suspeita de patrocínio, balada antes do jogo).
    
    Retorne EXATAMENTE UM JSON com esta estrutura (sem markdown ou formatação extra):
    {{
        "titulo": "Título Curto do Evento",
        "descricao": "A história do que aconteceu.",
        "opcao_A": {{
            "texto": "Ação agressiva ou focada na mídia.",
            "consequencia_tipo": "midia",
            "consequencia_valor": 5,
            "penalidade_tipo": "moral",
            "penalidade_valor": -5
        }},
        "opcao_B": {{
            "texto": "Ação apaziguadora ou focada no grupo.",
            "consequencia_tipo": "moral",
            "consequencia_valor": 5,
            "penalidade_tipo": "midia",
            "penalidade_valor": -2
        }}
    }}
    """
    
    # --- CÓDIGO REAL DA IA (Descomente quando tiver a API Key configurada) ---
    # model = genai.GenerativeModel('gemini-1.5-flash')
    # response = model.generate_content(prompt)
    # return json.loads(response.text)
    
    # --- MOCK PARA TESTES (Para você testar antes de plugar a IA) ---
    return {
        "titulo": "Fofoca no Vestiário",
        "descricao": f"Um jornalista publicou no Twitter que {avatar.nome_camisa} falou mal do treinador em um restaurante. O elenco todo está olhando torto para você no treino de hoje.",
        "opcao_A": {
            "texto": "Desmentir na internet e atacar o jornalista.",
            "consequencia_tipo": "midia",
            "consequencia_valor": 4,
            "penalidade_tipo": "moral",
            "penalidade_valor": -3
        },
        "opcao_B": {
            "texto": "Reunir o grupo e pedir desculpas pelo mal-entendido.",
            "consequencia_tipo": "moral",
            "consequencia_valor": 5,
            "penalidade_tipo": "fisico",
            "penalidade_valor": -2
        }
    }

def resolver_dilema(avatar, opcao_escolhida_dict):
    """
    Aplica os buffs e debuffs da escolha do jogador e salva no banco.
    """
    # Ex: { "consequencia_tipo": "midia", "consequencia_valor": 5, "penalidade_tipo": "moral", "penalidade_valor": -3 }
    
    # Aplica o bônus
    attr_ganho = opcao_escolhida_dict['consequencia_tipo']
    valor_ganho = opcao_escolhida_dict['consequencia_valor']
    if hasattr(avatar, attr_ganho):
        novo_valor = min(getattr(avatar, attr_ganho) + valor_ganho, 99)
        setattr(avatar, attr_ganho, novo_valor)

    # Aplica a penalidade
    attr_perda = opcao_escolhida_dict['penalidade_tipo']
    valor_perda = opcao_escolhida_dict['penalidade_valor'] # Vem negativo do JSON
    if hasattr(avatar, attr_perda):
        novo_valor = max(getattr(avatar, attr_perda) + valor_perda, 1) # Não deixa cair abaixo de 1
        setattr(avatar, attr_perda, novo_valor)

    avatar.save()


def gerar_calendario_liga(campeonato):
    """
    Algoritmo Round-Robin para gerar o calendário do campeonato de forma automática.
    """
    clubes = list(Clube.objects.filter(divisao=campeonato.divisao))
    
    # Se for ímpar, adicionamos um 'Bye' (Folga) fictício para balancear a matemática
    if len(clubes) % 2 != 0:
        clubes.append(None)
        
    total_clubes = len(clubes)
    total_rodadas = total_clubes - 1
    metade_tamanho = total_clubes // 2

    partidas_criadas = []

    # Turno (Ida)
    for rodada in range(total_rodadas):
        for i in range(metade_tamanho):
            casa = clubes[i]
            fora = clubes[total_clubes - 1 - i]
            
            if casa is not None and fora is not None:
                partidas_criadas.append(
                    PartidaMundo(campeonato=campeonato, clube_casa=casa, clube_fora=fora)
                )
                
        # Rotaciona os clubes (mantendo o primeiro fixo)
        clubes.insert(1, clubes.pop())

    # Returno (Volta) - Inverte os mandos de campo
    for rodada in range(total_rodadas):
        for i in range(metade_tamanho):
            fora = clubes[i] # O que era casa no turno, agora é fora
            casa = clubes[total_clubes - 1 - i]
            
            if casa is not None and fora is not None:
                partidas_criadas.append(
                    PartidaMundo(campeonato=campeonato, clube_casa=casa, clube_fora=fora)
                )
                
    PartidaMundo.objects.bulk_create(partidas_criadas)
    return True

def escalar_time_titular(clube):
    """
    IA do Treinador: Escala os 11 melhores jogadores do clube (Misturando Reais e Bots).
    Formação Base: 4-4-2
    """
    posicoes_taticas = [
        'GK', 'RB', 'CB', 'CB', 'LB', 
        'RM', 'CM', 'CM', 'LM', 
        'ST', 'ST'
    ]
    
    # Pega todos os avatares reais do clube saudáveis (sem lesão)
    elenco_real = list(Avatar.objects.filter(clube_atual=clube, lesionado_rodadas_restantes=0))
    
    # Ordena o elenco pelo mérito: OVR + (Moral/10)
    elenco_real.sort(key=lambda x: x.ovr_calculado + (x.moral / 10), reverse=True)
    
    # Limpa a prancheta atual do clube
    EscalacaoPosicao.objects.filter(clube=clube).delete()
    
    escalacao_salvar = []
    
    for posicao in posicoes_taticas:
        # Tenta achar um jogador real para a vaga
        jogador_escolhido = None
        if elenco_real:
            jogador_escolhido = elenco_real.pop(0) # Pega o melhor disponível
            
        if jogador_escolhido:
            # Jogador Real assume a posição
            escalacao_salvar.append(EscalacaoPosicao(
                clube=clube,
                posicao_campo=posicao,
                jogador_titular=jogador_escolhido
            ))
        else:
            # Não tem humano? A IA injeta um Bot Genérico para completar o time
            escalacao_salvar.append(EscalacaoPosicao(
                clube=clube,
                posicao_campo=posicao,
                jogador_titular=None,
                bot_nome=f"Base {clube.sigla} ({posicao})",
                bot_ovr=random.randint(55, 65) # OVR do bot
            ))
            
    EscalacaoPosicao.objects.bulk_create(escalacao_salvar)
    return True


def processar_tique_partida(partida):
    """
    Motor executado a cada chamada da API. Avança o tempo, verifica AFK
    e gera novos lances até chegar aos 90 minutos.
    """
    if partida.status == 'finalizada':
        return

    agora = timezone.now()

    # REGRA 1: TRATAR AFK (O tempo de decisão do jogador estourou)
    if partida.jogador_esperado and partida.vencimento_lance:
        if agora > partida.vencimento_lance:
            # Jogador não clicou a tempo. A IA assume (ação genérica/falha)
            partida.adicionar_log(f"{partida.jogador_esperado.nome_camisa} demorou muito para agir e perdeu a posse de bola!", destaque=True)
            partida.jogador_esperado = None
            partida.opcoes_lance = None
            partida.vencimento_lance = None
            partida.save()
        else:
            # O tempo ainda está rolando, a partida congela aguardando a ação
            return

    # REGRA 2: AVANÇAR O RELÓGIO (Simula 5 minutos a cada tique)
    partida.minuto_atual += 5
    
    if partida.minuto_atual > 90:
        partida.status = 'finalizada'
        partida.adicionar_log("FIM DE JOGO! O árbitro aponta para o centro do campo.", destaque=True)
        partida.save()
        return

    # REGRA 3: GERADOR DE LANCES (20% de chance de um lance chave a cada 5 minutos)
    if random.randint(1, 100) <= 20:
        gerar_lance_chave(partida)
    else:
        # Texto de transição para manter a tela viva
        textos_neutros = [
            "A bola rola no meio de campo sem muita objetividade.",
            "As defesas estão bem postadas, jogo truncado.",
            "Troca de passes laterais tentando encontrar espaços.",
            "Falta dura no meio campo, o juiz apenas adverte verbalmente."
        ]
        partida.adicionar_log(random.choice(textos_neutros))
        partida.save()

def gerar_lance_chave(partida):
    """ Sorteia um jogador real em campo para decidir uma jogada """
    from .models import EscalacaoPosicao
    
    # Busca titulares reais de ambos os times (Omitindo bots)
    titulares_casa = list(EscalacaoPosicao.objects.filter(clube=partida.clube_casa, jogador_titular__isnull=False))
    titulares_fora = list(EscalacaoPosicao.objects.filter(clube=partida.clube_fora, jogador_titular__isnull=False))
    
    todos_humanos = titulares_casa + titulares_fora
    
    if not todos_humanos:
        # Só tem bot em campo. A IA resolve sozinha e gera texto genérico.
        partida.adicionar_log("Chute perigoso de fora da área, mas a bola vai para fora!")
        return

    # Sorteia o humano que vai participar do lance
    escolhido = random.choice(todos_humanos).jogador_titular
    
    partida.adicionar_log(f"ATENÇÃO! A bola sobrou livre para {escolhido.nome_camisa} na entrada da área!", destaque=True)
    
    # Prepara a trava na partida e envia as opções para a tela
    partida.jogador_esperado = escolhido
    partida.opcoes_lance = {
        'A': 'Chutar Forte (Depende de Técnica)',
        'B': 'Tocar de Lado (Depende de Inteligência)',
        'C': 'Cavar o Pênalti (Risco Alto)'
    }
    partida.vencimento_lance = timezone.now() + timedelta(seconds=12) # 12 segundos para responder
    partida.save()

def resolver_acao_jogador(partida, avatar, escolha):
    """ Calcula o sucesso da decisão tomada pelo humano """
    sucesso = False
    
    # Lógica simplificada de resolução baseada no OVR
    dado = random.randint(1, 100)
    chance_sucesso = avatar.tecnica if escolha == 'A' else avatar.inteligencia
    
    if escolha == 'C': # Cavar pênalti (Risco maior)
        chance_sucesso = 30
        
    if dado <= chance_sucesso:
        sucesso = True
        
    eh_time_casa = (avatar.clube_atual == partida.clube_casa)
    
    if sucesso:
        texto = f"GOLAÇO! {avatar.nome_camisa} tomou a decisão perfeita e balançou as redes!"
        if eh_time_casa:
            partida.gols_casa += 1
        else:
            partida.gols_fora += 1
    else:
        texto = f"PERDEU! A decisão de {avatar.nome_camisa} não funcionou e a zaga cortou."
        
    partida.adicionar_log(texto, destaque=True)
    
    # Libera a partida para voltar a rodar
    partida.jogador_esperado = None
    partida.opcoes_lance = None
    partida.vencimento_lance = None
    partida.save()


def encerrar_partida_e_processar_stats(partida):
    from .models import EscalacaoPosicao
    
    titulares = EscalacaoPosicao.objects.filter(
        clube__in=[partida.clube_casa, partida.clube_fora],
        jogador_titular__isnull=False
    )

    vencedor = None
    if partida.gols_casa > partida.gols_fora: vencedor = partida.clube_casa
    elif partida.gols_fora > partida.gols_casa: vencedor = partida.clube_fora

    for escalacao in titulares:
        avatar = escalacao.jogador_titular
        
        # 1. CUSTO FÍSICO E LESÕES 
        avatar.fisico = max(avatar.fisico - 15, 1) 
        if avatar.fisico < 45:
            chance_lesao = (45 - avatar.fisico) 
            if random.randint(1, 100) <= chance_lesao:
                avatar.lesionado_rodadas_restantes = random.randint(1, 3) 
        
        # 2. CÁLCULO DA NOTA (Rating)
        nota = round(random.uniform(5.5, 7.5), 1)
        if avatar.clube_atual == vencedor:
            nota += round(random.uniform(1.0, 2.0), 1) 
            
        # 3. SETA DE MOMENTO E XP
        if nota >= 8.0:
            avatar.seta_momento = 2 
            avatar.xp_disponivel += 50
        elif nota < 6.0:
            avatar.seta_momento = -2
            avatar.xp_disponivel += 10
        else:
            avatar.seta_momento = 0 
            avatar.xp_disponivel += 25
            
        # 4. A QUEBRA DO TETO (Milagre)
        if avatar.ovr_calculado >= avatar.teto_potencial_oculto and nota >= 8.5:
            avatar.teto_potencial_oculto += 2 
            
        # ==========================================
        # 5. ECONOMIA: O PAGAMENTO (NOVO)
        # ==========================================
        # Utiliza 'salario_semanal' ou o nome exato que está no seu model Avatar
        salario = getattr(avatar, 'salario_semanal', 1000) 
        
        # Lógica preparada para futuros patrocínios (pode expandir isto depois)
        renda_extra_patrocinios = 0 
        
        # Bónus de Vitória (Bicho)
        bicho = 0
        if avatar.clube_atual == vencedor:
            bicho = int(salario * 0.20) # Recebe +20% do salário se ganhar o jogo
            
        # O dinheiro entra na conta do jogador
        avatar.saldo_bancario += (salario + renda_extra_patrocinios + bicho)

        # Finalmente, guarda tudo na base de dados
        avatar.save()

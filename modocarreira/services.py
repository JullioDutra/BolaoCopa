import json
import random
from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
import google.generativeai as genai

# Importação dos modelos (Certifique-se de que todos estes existem no seu models.py)
from .models import (
    Avatar, Clube, ServidorConfig, PartidaMundo, EscalacaoPosicao, 
    ConflitoVestiario, Campeonato, PropostaJanela, RegistroHistoricoCampeao, 
    ConvocacaoSelecao, ClassificacaoLiga, NoticiaJornal
)

# ==========================================
# 1. CONFIGURAÇÃO E FUNÇÕES DA IA (GEMINI)
# ==========================================

# genai.configure(api_key=settings.GEMINI_API_KEY)

def obter_modelo_gemini(formato_json=False):
    """ Retorna a instância do Gemini otimizada (Força JSON se necessário) """
    config = {"response_mime_type": "application/json"} if formato_json else None
    return genai.GenerativeModel('gemini-1.5-flash', generation_config=config)

def gerar_dilema_ia(avatar):
    clube_nome = avatar.clube_atual.nome if avatar.clube_atual else "clube de várzea"
    prompt = f"""
    Você é o mestre de um RPG de futebol. Crie um evento aleatório (dilema) que aconteceu hoje com o jogador {avatar.nome_camisa}, que tem {avatar.idade_atual} anos e joga como {avatar.get_arquetipo_display()} no {clube_nome}.
    O evento deve ser realista, curto e focado em bastidores (imprensa, vestiário, noitada, torcida).
    
    Você DEVE retornar APENAS um JSON válido com esta estrutura:
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
        modelo = obter_modelo_gemini(formato_json=True)
        resposta = modelo.generate_content(prompt)
        return json.loads(resposta.text)
    except Exception as e:
        return {
            "titulo": "Fofoca de Corredor",
            "descricao": f"Vazou um boato de que {avatar.nome_camisa} está forçando uma saída do {clube_nome}. A torcida está cobrando explicações.",
            "opcao_A": { "texto": "Fazer uma live alimentando o boato.", "consequencia_tipo": "media_fama", "consequencia_valor": 5, "penalidade_tipo": "moral", "penalidade_valor": -10 },
            "opcao_B": { "texto": "Beijar o escudo no próximo treino.", "consequencia_tipo": "moral", "consequencia_valor": 8, "penalidade_tipo": "media_fama", "penalidade_valor": -2 }
        }

def gerar_frases_narracao_ia(clube_casa, clube_fora):
    prompt = f'Crie 10 frases curtas (máx 12 palavras) de narração de rádio de futebol para um jogo entre {clube_casa} e {clube_fora}. Retorne EXATAMENTE um array JSON de strings.'
    try:
        modelo = obter_modelo_gemini(formato_json=True)
        resposta = modelo.generate_content(prompt)
        return json.loads(resposta.text)
    except Exception:
        return [
            f"O {clube_casa} tenta dominar o meio-campo.",
            f"A defesa do {clube_fora} está muito bem postada hoje.",
            "Troca de passes burocrática neste momento.",
            "O treinador pede mais intensidade na marcação!",
            "Lançamento longo, mas a bola sai pela linha lateral."
        ]

def gerar_motivo_treta_ia(nome_ofensor, nome_ofendido):
    prompt = f"Crie um motivo criativo e muito curto (máximo 15 palavras) explicando o porquê do jogador {nome_ofensor} ter brigado com {nome_ofendido} no balneário após a derrota."
    try:
        modelo = obter_modelo_gemini()
        resposta = modelo.generate_content(prompt)
        return resposta.text.strip().replace('"', '')
    except Exception:
        return f"{nome_ofensor} culpou {nome_ofendido} pelo golo sofrido e atirou-lhe uma chuteira."

def gerar_laudo_medico_ia(nome_jogador):
    prompt = f"O jogador {nome_jogador} lesionou-se durante um jogo de futebol. Crie um diagnóstico médico curto (máximo 12 palavras). Ex: Estiramento na coxa após tentar um elástico."
    try:
        modelo = obter_modelo_gemini()
        resposta = modelo.generate_content(prompt)
        return resposta.text.strip().replace('"', '')
    except Exception:
        return "Rotura muscular na coxa direita devido a fadiga extrema."

def gerar_noticia_jornal_ia(clube_casa, gols_casa, clube_fora, gols_fora, heroi=None):
    texto_heroi = f"O grande destaque foi {heroi}." if heroi else ""
    prompt = f"""
    Escreva uma notícia de jornal sensacionalista de futebol sobre o jogo: {clube_casa} {gols_casa} x {gols_fora} {clube_fora}. {texto_heroi}
    Retorne UM JSON com:
    {{
        "manchete": "Título Chamativo (máx 10 palavras)",
        "corpo": "Texto da notícia com 3 frases divertidas e sensacionalistas."
    }}
    """
    try:
        modelo = obter_modelo_gemini(formato_json=True)
        resposta = modelo.generate_content(prompt)
        return json.loads(resposta.text)
    except Exception:
        return {
            "manchete": f"Fim de Papo: {clube_casa} e {clube_fora} dão espetáculo!",
            "corpo": f"A partida terminou {gols_casa} a {gols_fora}. Os adeptos já comentam nas redes sociais sobre o desempenho das equipas, exigindo melhorias para a próxima rodada."
        }


# ==========================================
# 2. FUNDAÇÃO (CRIAÇÃO DO AVATAR E PENEIRA)
# ==========================================

def calcular_dna_inicial(arquetipo):
    dna = {'fisico': 60, 'tecnica': 60, 'inteligencia': 60, 'midia': 20}
    if arquetipo == 'xerife': dna.update({'fisico': 75, 'tecnica': 45, 'inteligencia': 65, 'midia': 15})
    elif arquetipo == 'maestro': dna.update({'fisico': 50, 'tecnica': 70, 'inteligencia': 75, 'midia': 25})
    elif arquetipo == 'matador': dna.update({'fisico': 65, 'tecnica': 75, 'inteligencia': 55, 'midia': 40})
    elif arquetipo == 'motorzinho': dna.update({'fisico': 60, 'tecnica': 65, 'inteligencia': 50, 'midia': 50})
    return dna

def calcular_teto_potencial():
    sorte = random.randint(1, 100)
    if sorte <= 10: return random.randint(88, 94) 
    elif sorte <= 30: return random.randint(82, 87) 
    elif sorte <= 70: return random.randint(76, 81) 
    else: return random.randint(70, 75) 

def sortear_clube_peneira():
    sorte = random.randint(1, 100)
    if sorte <= 70: divisao = 'C'
    elif sorte <= 90: divisao = 'B'
    else: divisao = 'A'

    clubes_disponiveis = Clube.objects.filter(divisao=divisao)
    if not clubes_disponiveis.exists():
        clubes_disponiveis = Clube.objects.all()
    
    if clubes_disponiveis.exists():
        return random.choice(clubes_disponiveis)
    return None

@transaction.atomic
def criar_avatar_peneira(usuario, nome_camisa, arquetipo):
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


# ==========================================
# 3. ROTINA E TREINOS
# ==========================================

def checar_gatilho_dilema():
    return random.randint(1, 100) <= 30

def processar_treino(avatar, tipo_treino):
    if avatar.pontos_acao_diarios <= 0:
        raise ValueError("Você não tem Pontos de Ação (Energia) suficientes hoje.")

    avatar.pontos_acao_diarios -= 1
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

    if atributo != 'media_fama' and avatar.ovr_calculado >= avatar.teto_potencial_oculto:
        avatar.xp_disponivel += 10 
    else:
        novo_valor = min(valor_atual + valor_ganho, 99)
        setattr(avatar, atributo, novo_valor)

    avatar.save()
    return {
        'atributo_treinado': atributo,
        'valor_ganho': valor_ganho,
        'novo_ovr': avatar.ovr_calculado,
        'ap_restante': avatar.pontos_acao_diarios
    }

def resolver_dilema(avatar, opcao_escolhida_dict):
    attr_ganho = opcao_escolhida_dict['consequencia_tipo']
    valor_ganho = opcao_escolhida_dict['consequencia_valor']
    if hasattr(avatar, attr_ganho):
        setattr(avatar, attr_ganho, min(getattr(avatar, attr_ganho) + valor_ganho, 99))

    attr_perda = opcao_escolhida_dict['penalidade_tipo']
    valor_perda = opcao_escolhida_dict['penalidade_valor']
    if hasattr(avatar, attr_perda):
        setattr(avatar, attr_perda, max(getattr(avatar, attr_perda) + valor_perda, 1))
    
    avatar.save()


# ==========================================
# 4. PARTIDAS E LIGAS (PRÉ, DURANTE E PÓS)
# ==========================================

def gerar_calendario_liga(campeonato):
    clubes = list(Clube.objects.filter(divisao=campeonato.divisao))
    if len(clubes) % 2 != 0: clubes.append(None)
        
    total_clubes = len(clubes)
    total_rodadas = total_clubes - 1
    metade_tamanho = total_clubes // 2
    partidas_criadas = []

    for rodada in range(total_rodadas):
        for i in range(metade_tamanho):
            casa = clubes[i]
            fora = clubes[total_clubes - 1 - i]
            if casa is not None and fora is not None:
                partidas_criadas.append(PartidaMundo(campeonato=campeonato, clube_casa=casa, clube_fora=fora))
        clubes.insert(1, clubes.pop())

    for rodada in range(total_rodadas):
        for i in range(metade_tamanho):
            fora = clubes[i] 
            casa = clubes[total_clubes - 1 - i]
            if casa is not None and fora is not None:
                partidas_criadas.append(PartidaMundo(campeonato=campeonato, clube_casa=casa, clube_fora=fora))
                
    PartidaMundo.objects.bulk_create(partidas_criadas)
    return True

def escalar_time_titular(clube):
    posicoes_taticas = ['GK', 'RB', 'CB', 'CB', 'LB', 'RM', 'CM', 'CM', 'LM', 'ST', 'ST']
    elenco_real = list(Avatar.objects.filter(clube_atual=clube, lesionado_rodadas_restantes=0))
    elenco_real.sort(key=lambda x: x.ovr_calculado + (x.moral / 10), reverse=True)
    
    EscalacaoPosicao.objects.filter(clube=clube).delete()
    escalacao_salvar = []
    
    for posicao in posicoes_taticas:
        jogador_escolhido = elenco_real.pop(0) if elenco_real else None
        if jogador_escolhido:
            escalacao_salvar.append(EscalacaoPosicao(clube=clube, posicao_campo=posicao, jogador_titular=jogador_escolhido))
        else:
            escalacao_salvar.append(EscalacaoPosicao(clube=clube, posicao_campo=posicao, bot_nome=f"Base {clube.sigla} ({posicao})", bot_ovr=random.randint(55, 65)))
            
    EscalacaoPosicao.objects.bulk_create(escalacao_salvar)
    return True

def processar_tique_partida(partida):
    if partida.status == 'finalizada': return
    agora = timezone.now()

    if partida.jogador_esperado and partida.vencimento_lance:
        if agora > partida.vencimento_lance:
            partida.adicionar_log(f"{partida.jogador_esperado.nome_camisa} demorou muito para agir e perdeu a posse de bola!", destaque=True)
            partida.jogador_esperado = None
            partida.opcoes_lance = None
            partida.vencimento_lance = None
            partida.save()
        else:
            return

    partida.minuto_atual += 5
    if partida.minuto_atual > 90:
        partida.status = 'finalizada'
        partida.adicionar_log("FIM DE JOGO! O árbitro aponta para o centro do campo.", destaque=True)
        partida.save()
        return

    if random.randint(1, 100) <= 20:
        gerar_lance_chave(partida)
    else:
        # Puxa frase da IA gerada no apito inicial (fallback caso esteja vazio)
        frases = partida.frases_narracao_ia if partida.frases_narracao_ia else ["Bola rolando no meio campo..."]
        partida.adicionar_log(random.choice(frases))
        partida.save()

def gerar_lance_chave(partida):
    titulares_casa = list(EscalacaoPosicao.objects.filter(clube=partida.clube_casa, jogador_titular__isnull=False))
    titulares_fora = list(EscalacaoPosicao.objects.filter(clube=partida.clube_fora, jogador_titular__isnull=False))
    todos_humanos = titulares_casa + titulares_fora
    
    if not todos_humanos:
        partida.adicionar_log("Chute perigoso de fora da área, mas a bola vai para fora!")
        return

    escolhido = random.choice(todos_humanos).jogador_titular
    partida.adicionar_log(f"ATENÇÃO! A bola sobrou livre para {escolhido.nome_camisa} na entrada da área!", destaque=True)
    
    partida.jogador_esperado = escolhido
    partida.opcoes_lance = {
        'A': 'Chutar Forte (Depende de Técnica)',
        'B': 'Tocar de Lado (Depende de Inteligência)',
        'C': 'Cavar o Pênalti (Risco Alto)'
    }
    partida.vencimento_lance = timezone.now() + timedelta(seconds=12)
    partida.save()

def resolver_acao_jogador(partida, avatar, escolha):
    sucesso = False
    dado = random.randint(1, 100)
    chance_sucesso = avatar.tecnica if escolha == 'A' else avatar.inteligencia
    if escolha == 'C': chance_sucesso = 30
        
    if dado <= chance_sucesso: sucesso = True
        
    eh_time_casa = (avatar.clube_atual == partida.clube_casa)
    if sucesso:
        texto = f"GOLAÇO! {avatar.nome_camisa} tomou a decisão perfeita e balançou as redes!"
        if eh_time_casa: partida.gols_casa += 1
        else: partida.gols_fora += 1
    else:
        texto = f"PERDEU! A decisão de {avatar.nome_camisa} não funcionou e a zaga cortou."
        
    partida.adicionar_log(texto, destaque=True)
    partida.jogador_esperado = None
    partida.opcoes_lance = None
    partida.vencimento_lance = None
    partida.save()

def encerrar_partida_e_processar_stats(partida):
    titulares = EscalacaoPosicao.objects.filter(
        clube__in=[partida.clube_casa, partida.clube_fora],
        jogador_titular__isnull=False
    )

    vencedor = None
    if partida.gols_casa > partida.gols_fora: vencedor = partida.clube_casa
    elif partida.gols_fora > partida.gols_casa: vencedor = partida.clube_fora

    for escalacao in titulares:
        avatar = escalacao.jogador_titular
        
        # 1. CUSTO FÍSICO E LESÕES (Com IA)
        avatar.fisico = max(avatar.fisico - 15, 1) 
        if avatar.fisico < 45:
            chance_lesao = (45 - avatar.fisico) 
            if random.randint(1, 100) <= chance_lesao:
                avatar.lesionado_rodadas_restantes = random.randint(1, 3) 
                avatar.descricao_lesao = gerar_laudo_medico_ia(avatar.nome_camisa)
            else:
                avatar.descricao_lesao = None
        
        # 2. CÁLCULO DA NOTA
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
            
        # 4. A QUEBRA DO TETO
        if avatar.ovr_calculado >= avatar.teto_potencial_oculto and nota >= 8.5:
            avatar.teto_potencial_oculto += 2 
            
        # 5. ECONOMIA: O PAGAMENTO (Salários e Patrocínios)
        salario = getattr(avatar, 'salario_semanal', 1000) 
        renda_extra_patrocinios = 0 
        bicho = int(salario * 0.20) if avatar.clube_atual == vencedor else 0
        avatar.saldo_bancario += (salario + renda_extra_patrocinios + bicho)

        avatar.save()
        
    # Gera conflitos pós-jogo se houver base para isso
    gerar_treta_pos_jogo(partida)

# ==========================================
# 5. VIDA SOCIAL E VESTIÁRIO
# ==========================================

def gerar_treta_pos_jogo(partida):
    humanos_casa = list(Avatar.objects.filter(clube_atual=partida.clube_casa, vaga_titular__isnull=False))
    humanos_fora = list(Avatar.objects.filter(clube_atual=partida.clube_fora, vaga_titular__isnull=False))
    
    times_tropecaram = []
    if partida.gols_casa < partida.gols_fora: times_tropecaram.append(humanos_casa)
    elif partida.gols_fora < partida.gols_casa: times_tropecaram.append(humanos_fora)
    else: 
        times_tropecaram.append(humanos_casa)
        times_tropecaram.append(humanos_fora)
        
    for elenco in times_tropecaram:
        if len(elenco) >= 2 and random.randint(1, 100) <= 40:
            ofensor = random.choice(elenco)
            ofendido = random.choice([j for j in elenco if j != ofensor])
            ja_brigados = ConflitoVestiario.objects.filter(atleta_ofensor=ofensor, atleta_ofendido=ofendido, ativo=True).exists()
            
            if not ja_brigados:
                motivo_ia = gerar_motivo_treta_ia(ofensor.nome_camisa, ofendido.nome_camisa)
                ConflitoVestiario.objects.create(atleta_ofensor=ofensor, atleta_ofendido=ofendido, descricao_fato=motivo_ia, ativo=True)

def fazer_as_pazes(avatar, conflito_id):
    conflito = ConflitoVestiario.objects.get(id=conflito_id)
    if avatar.pontos_acao_diarios <= 0:
        raise ValueError("Você não tem Energia (AP) suficiente.")
        
    avatar.pontos_acao_diarios -= 1
    avatar.save()
    conflito.ativo = False
    conflito.save()
    return True

# ==========================================
# 6. MERCADO DA BOLA E TRANSFERÊNCIAS
# ==========================================

def calcular_valor_passe(avatar):
    base = (avatar.ovr_calculado ** 2) * 500
    idade = avatar.idade_atual
    if idade <= 21: fator_idade = 1.5
    elif idade >= 30: fator_idade = 0.6
    else: fator_idade = 1.0
    fator_midia = 1.0 + (avatar.media_fama / 100.0)
    return int(base * fator_idade * fator_midia)

def gerar_propostas_mercado(avatar):
    if PropostaJanela.objects.filter(avatar=avatar, status='analise').exists(): return False
    valor_passe = calcular_valor_passe(avatar)
    ovr = avatar.ovr_calculado
    
    if ovr >= 80: divisao_alvo = ['A', 'INT']
    elif ovr >= 70: divisao_alvo = ['A', 'B']
    else: divisao_alvo = ['B', 'C']
        
    clubes_interessados = Clube.objects.filter(divisao__in=divisao_alvo).exclude(id=avatar.clube_atual.id).order_by('?')[:2]
    for clube in clubes_interessados:
        salario = int(ovr * 250 * random.uniform(0.9, 1.2))
        PropostaJanela.objects.create(
            avatar=avatar, clube_comprador=clube, clube_vendedor=avatar.clube_atual,
            valor_transferencia=valor_passe, salario_proposto=salario, status='analise'
        )
    return True

def processar_resposta_proposta(proposta_id, avatar, acao):
    proposta = PropostaJanela.objects.get(id=proposta_id, avatar=avatar)
    if acao == 'aceitar':
        proposta.status = 'concluida'
        avatar.clube_atual = proposta.clube_comprador
        avatar.salario_semanal = proposta.salario_proposto
        avatar.moral = 100 
        avatar.save()
        PropostaJanela.objects.filter(avatar=avatar, status='analise').exclude(id=proposta_id).update(status='vetada_jogador')
    elif acao == 'recusar':
        proposta.status = 'vetada_jogador'
        avatar.moral = min(avatar.moral + 15, 100)
        avatar.save()
    proposta.save()

# ==========================================
# 7. O FIM DOS TEMPOS (VIRADA DE TEMPORADA)
# ==========================================

@transaction.atomic
def executar_virada_de_temporada():
    config = ServidorConfig.objects.first()
    if not config: return False
    temporada_alvo = config.temporada_atual
    
    campeonatos_ativos = Campeonato.objects.filter(temporada=temporada_alvo, tipo='liga')
    for camp in campeonatos_ativos:
        tabela = ClassificacaoLiga.objects.filter(campeonato=camp).order_by('-pontos', '-vitorias', '-gols_pro')
        if not tabela.exists(): continue
            
        campeao = tabela.first().clube
        vice = tabela[1].clube if tabela.count() > 1 else None
        
        RegistroHistoricoCampeao.objects.create(
            temporada=temporada_alvo,
            campeonato_nome=f"{camp.nome} (Série {camp.divisao})",
            clube_campeao_nome=campeao.nome,
            clube_vice_nome=vice.nome if vice else "N/A",
            artilheiro_temporada_nome="Gerar pelo Banco",
            artilheiro_gols_totais=0,
            mvp_temporada_nome="Definir MVP",
            mvp_nota_media_final=8.5,
            snapshot_elenco_selecao=json.dumps({"selecao": []}) 
        )

    todos_avatares = Avatar.objects.all().order_by('-fisico', '-tecnica', '-media_fama') 
    convocados = []
    lista_json_selecao = []
    
    for avatar in todos_avatares[:23]: 
        pontuacao = avatar.ovr_calculado + (avatar.media_fama * 0.2)
        convocados.append(ConvocacaoSelecao(temporada=temporada_alvo, avatar=avatar, pontuacao_ranking_calculada=pontuacao))
        lista_json_selecao.append({
            "nome": avatar.nome_camisa,
            "ovr_epoca": avatar.ovr_calculado,
            "clube_epoca": avatar.clube_atual.nome if avatar.clube_atual else "Sem Clube"
        })
        
    ConvocacaoSelecao.objects.bulk_create(convocados)
    RegistroHistoricoCampeao.objects.filter(temporada=temporada_alvo, campeonato_nome__contains="Série A").update(
        snapshot_elenco_selecao=json.dumps({"selecao": lista_json_selecao})
    )

    for avatar in Avatar.objects.all():
        idade_futura = avatar.idade_inicial + ((temporada_alvo + 1) - avatar.temporada_nascimento)
        if idade_futura >= 32:
            avatar.fisico = max(avatar.fisico - 3, 10)
            avatar.tecnica = max(avatar.tecnica - 2, 10)
            avatar.inteligencia = min(avatar.inteligencia + 2, 99)
            
        avatar.seta_momento = 0
        avatar.lesionado_rodadas_restantes = 0
        avatar.xp_disponivel += 100 
        avatar.save()
        
    PartidaMundo.objects.filter(campeonato__temporada=temporada_alvo).delete()
    
    config.temporada_atual += 1
    config.rodada_atual = 1
    config.fase_mercado_aberto = True 
    config.save()
    return True

def processar_substituicoes(partida):
    """
    Motor do 2º Tempo: Substitui Bots e Titulares cansados por Humanos do Banco.
    Executado aos 60 e 75 minutos.
    """
    from .models import EscalacaoPosicao, Avatar
    
    houve_sub = False
    for clube in [partida.clube_casa, partida.clube_fora]:
        # 1. Quem são os Humanos que estão atualmente em campo?
        titulares_ids = EscalacaoPosicao.objects.filter(
            clube=clube, jogador_titular__isnull=False
        ).values_list('jogador_titular_id', flat=True)
        
        # 2. Quem são os Humanos que estão no Banco (Saudáveis)?
        reservas = list(Avatar.objects.filter(
            clube_atual=clube, lesionado_rodadas_restantes=0
        ).exclude(id__in=titulares_ids))
        
        if not reservas:
            continue # Não há jogadores humanos no banco para entrar
            
        # Ordena o banco do melhor para o pior (OVR)
        reservas.sort(key=lambda x: x.ovr_calculado, reverse=True)
        
        # 3. Quem deve sair? (Alvos)
        # Prioridade 1: Tirar os Bots (para dar espaço aos jogadores reais)
        alvos_bots = list(EscalacaoPosicao.objects.filter(clube=clube, jogador_titular__isnull=True))
        
        # Prioridade 2: Tirar Titulares Humanos Cansados (Físico menor que 50)
        alvos_cansados = list(EscalacaoPosicao.objects.filter(
            clube=clube, jogador_titular__fisico__lt=50
        ).order_by('jogador_titular__fisico'))
        
        alvos_substituicao = alvos_bots + alvos_cansados
        
        # 4. Fazer a troca na Prancheta (Máximo de 2 substituições por minuto de pausa)
        subs_feitas = 0
        while reservas and alvos_substituicao and subs_feitas < 2:
            reserva = reservas.pop(0)
            alvo = alvos_substituicao.pop(0)
            
            nome_saindo = alvo.jogador_titular.nome_camisa if alvo.jogador_titular else alvo.bot_nome
            
            # Atualiza a posição no campo com o novo jogador
            alvo.jogador_titular = reserva
            alvo.bot_nome = "" # Apaga o nome do bot, caso fosse um bot
            alvo.save()
            
            partida.adicionar_log(f"🔄 ALTERAÇÃO NO {clube.sigla}: Sai {nome_saindo}, entra {reserva.nome_camisa} com gás total!", destaque=False)
            
            houve_sub = True
            subs_feitas += 1
            
    if houve_sub:
        partida.save()

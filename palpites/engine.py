from .models import PalpiteLongoPrazo, Temporada

def processar_pontuacoes_longo_prazo(temporada_ano, classificacao_br, id_campeao_europa, id_campeao_cdb):
    """
    Função (Engine) para calcular os pontos de longo prazo dos usuários.
    
    Como passar os dados:
    - temporada_ano: Inteiro (ex: 2026)
    - classificacao_br: Dicionário com a posição real e o ID do Clube.
        Exemplo: {1: 12, 2: 5, 3: 8, 4: 10, ..., 17: 2, 18: 4, 19: 7, 20: 1}
        (Onde a chave é a posição final e o valor é o ID do time no banco)
    - id_campeao_europa: ID do clube que ganhou a Champions
    - id_campeao_cdb: ID do clube que ganhou a Copa do Brasil
    """
    try:
        temporada = Temporada.objects.get(ano=temporada_ano, ativa=True)
    except Temporada.DoesNotExist:
        print("Temporada ativa não encontrada!")
        return False

    # Busca todos os palpites de longo prazo desta temporada
    palpites = PalpiteLongoPrazo.objects.filter(temporada=temporada)

    for palpite in palpites:
        pontos = 0
        clube_id = palpite.clube.id
        
        # ==========================================
        # 1. CAMPEÃO DO BRASILEIRÃO (50 pts)
        # ==========================================
        if palpite.tipo == 'CAMPEAO_BR':
            if classificacao_br.get(1) == clube_id:
                pontos = 50
        
        # ==========================================
        # 2. G4 DO BRASILEIRÃO (30 pts ou 40 pts exatos)
        # ==========================================
        elif palpite.tipo == 'G4':
            # Descobre em qual posição o time apostado terminou de verdade
            posicao_real = None
            for pos, cid in classificacao_br.items():
                if cid == clube_id:
                    posicao_real = pos
                    break
            
            if posicao_real and posicao_real <= 4:
                if palpite.posicao_esperada == posicao_real:
                    pontos = 40  # Acertou em cheio a posição (ex: apostou que seria 2º e foi 2º)
                else:
                    pontos = 30  # Acertou apenas que estaria no G4, mas na posição errada
        
        # ==========================================
        # 3. Z4 DO BRASILEIRÃO (30 pts ou 35 pts exatos)
        # ==========================================
        elif palpite.tipo == 'Z4':
            posicao_real = None
            for pos, cid in classificacao_br.items():
                if cid == clube_id:
                    posicao_real = pos
                    break
            
            if posicao_real and posicao_real >= 17:
                if palpite.posicao_esperada == posicao_real:
                    pontos = 35  # Acertou em cheio a posição no rebaixamento
                else:
                    pontos = 30  # Acertou apenas que foi rebaixado
        
        # ==========================================
        # 4. CAMPEÃO EUROPEU (45 pts)
        # ==========================================
        elif palpite.tipo == 'CAMPEAO_EUROPA':
            if clube_id == id_campeao_europa:
                pontos = 45
                
        # ==========================================
        # 5. CAMPEÃO COPA DO BRASIL (50 pts)
        # ==========================================
        elif palpite.tipo == 'CAMPEAO_CDB':
            if clube_id == id_campeao_cdb:
                pontos = 50

        # Atualiza os pontos e salva no banco de dados
        if palpite.pontos_obtidos != pontos:
            palpite.pontos_obtidos = pontos
            palpite.save()

    print(f"✅ Pontuações de longo prazo processadas para a temporada {temporada.ano}!")
    return True

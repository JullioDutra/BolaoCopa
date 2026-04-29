from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 9: Esquadrões de Ouro e os Globetrotters da Bola'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 9 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Flamengo 2019 (Ano Mágico)",
                "jogadores": [
                    {"nome": "Diego Alves", "posicao": "Goleiro"}, 
                    {"nome": "Rafinha", "posicao": "Lateral Direito"},
                    {"nome": "Rodrigo Caio", "posicao": "Zagueiro"}, 
                    {"nome": "Pablo Marí", "posicao": "Zagueiro"},
                    {"nome": "Filipe Luís", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Willian Arão", "posicao": "Volante"},
                    {"nome": "Gerson", "posicao": "Meia Central"}, 
                    {"nome": "Everton Ribeiro", "posicao": "Meia-Atacante"},
                    {"nome": "De Arrascaeta", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Bruno Henrique", "posicao": "Segundo Atacante"},
                    {"nome": "Gabigol", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Corinthians 2012 (Mundial Invicto)",
                "jogadores": [
                    {"nome": "Cássio", "posicao": "Goleiro"}, 
                    {"nome": "Alessandro", "posicao": "Lateral Direito"},
                    {"nome": "Chicão", "posicao": "Zagueiro"}, 
                    {"nome": "Paulo André", "posicao": "Zagueiro"},
                    {"nome": "Fábio Santos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Ralf", "posicao": "Volante"},
                    {"nome": "Paulinho", "posicao": "Meia Central"}, 
                    {"nome": "Danilo", "posicao": "Meia-Atacante"},
                    {"nome": "Jorge Henrique", "posicao": "Ponta Direita"}, 
                    {"nome": "Emerson Sheik", "posicao": "Ponta Esquerda"},
                    {"nome": "Paolo Guerrero", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Palmeiras 1999 (Campeão da América)",
                "jogadores": [
                    {"nome": "Marcos", "posicao": "Goleiro"}, 
                    {"nome": "Arce", "posicao": "Lateral Direito"},
                    {"nome": "Roque Júnior", "posicao": "Zagueiro"}, 
                    {"nome": "Júnior Baiano", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "César Sampaio", "posicao": "Volante"},
                    {"nome": "Galeano", "posicao": "Volante"}, 
                    {"nome": "Zinho", "posicao": "Meia Esquerda"},
                    {"nome": "Alex", "posicao": "Meia-Atacante"}, 
                    {"nome": "Paulo Nunes", "posicao": "Segundo Atacante"},
                    {"nome": "Oséas", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Brasil 1982 (O Futebol Arte)",
                "jogadores": [
                    {"nome": "Valdir Peres", "posicao": "Goleiro"}, 
                    {"nome": "Leandro", "posicao": "Lateral Direito"},
                    {"nome": "Oscar", "posicao": "Zagueiro"}, 
                    {"nome": "Luizinho", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Toninho Cerezo", "posicao": "Volante"},
                    {"nome": "Falcão", "posicao": "Meia Central"}, 
                    {"nome": "Sócrates", "posicao": "Meia Direita"},
                    {"nome": "Zico", "posicao": "Meia-Atacante"}, 
                    {"nome": "Éder", "posicao": "Ponta Esquerda"},
                    {"nome": "Serginho Chulapa", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Milan 2006/07 (O Milan de Kaká)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, 
                    {"nome": "Oddo", "posicao": "Lateral Direito"},
                    {"nome": "Nesta", "posicao": "Zagueiro"}, 
                    {"nome": "Maldini", "posicao": "Zagueiro"},
                    {"nome": "Jankulovski", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Gattuso", "posicao": "Volante"},
                    {"nome": "Ambrosini", "posicao": "Volante"}, 
                    {"nome": "Pirlo", "posicao": "Meia Central"},
                    {"nome": "Seedorf", "posicao": "Meia Esquerda"}, 
                    {"nome": "Kaká", "posicao": "Meia-Atacante"},
                    {"nome": "Inzaghi", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Manchester United 2007/08 (Trio Mortal)",
                "jogadores": [
                    {"nome": "Van der Sar", "posicao": "Goleiro"}, 
                    {"nome": "Wes Brown", "posicao": "Lateral Direito"},
                    {"nome": "Ferdinand", "posicao": "Zagueiro"}, 
                    {"nome": "Vidic", "posicao": "Zagueiro"},
                    {"nome": "Evra", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Carrick", "posicao": "Volante"},
                    {"nome": "Scholes", "posicao": "Meia Central"}, 
                    {"nome": "Giggs", "posicao": "Meia Esquerda"},
                    {"nome": "Cristiano Ronaldo", "posicao": "Ponta Direita"}, 
                    {"nome": "Wayne Rooney", "posicao": "Segundo Atacante"},
                    {"nome": "Carlos Tevez", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Inter de Milão 2009/10 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Júlio César", "posicao": "Goleiro"}, 
                    {"nome": "Maicon", "posicao": "Lateral Direito"},
                    {"nome": "Lúcio", "posicao": "Zagueiro"}, 
                    {"nome": "Samuel", "posicao": "Zagueiro"},
                    {"nome": "Zanetti", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Cambiasso", "posicao": "Volante"},
                    {"nome": "Thiago Motta", "posicao": "Meia Central"}, 
                    {"nome": "Sneijder", "posicao": "Meia-Atacante"},
                    {"nome": "Pandev", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Samuel Eto'o", "posicao": "Ponta Direita"},
                    {"nome": "Diego Milito", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Fluminense 2012 (Máquina Tricolor)",
                "jogadores": [
                    {"nome": "Diego Cavalieri", "posicao": "Goleiro"}, 
                    {"nome": "Bruno", "posicao": "Lateral Direito"},
                    {"nome": "Gum", "posicao": "Zagueiro"}, 
                    {"nome": "Leandro Euzébio", "posicao": "Zagueiro"},
                    {"nome": "Carlinhos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Edinho", "posicao": "Volante"},
                    {"nome": "Jean", "posicao": "Volante"}, 
                    {"nome": "Deco", "posicao": "Meia Central"},
                    {"nome": "Thiago Neves", "posicao": "Meia-Atacante"}, 
                    {"nome": "Wellington Nem", "posicao": "Segundo Atacante"},
                    {"nome": "Fred", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Espanha 2010 (Tiki-Taka Campeão)",
                "jogadores": [
                    {"nome": "Casillas", "posicao": "Goleiro"}, 
                    {"nome": "Sergio Ramos", "posicao": "Lateral Direito"},
                    {"nome": "Piqué", "posicao": "Zagueiro"}, 
                    {"nome": "Puyol", "posicao": "Zagueiro"},
                    {"nome": "Capdevila", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Busquets", "posicao": "Volante"},
                    {"nome": "Xabi Alonso", "posicao": "Volante"}, 
                    {"nome": "Xavi", "posicao": "Meia Central"},
                    {"nome": "Iniesta", "posicao": "Meia-Atacante"}, 
                    {"nome": "Pedro", "posicao": "Ponta Direita"},
                    {"nome": "David Villa", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 9 (OS GLOBETROTTERS DA BOLA)
        # ==========================================
        trajetorias = [
            {
                "titulo": "A Patada Atômica",
                "resposta_oculta": "roberto carlos",
                "clubes": ["União São João", "Palmeiras", "Inter de Milão", "Real Madrid", "Fenerbahçe", "Corinthians", "Anzhi", "Delhi Dynamos"]
            },
            {
                "titulo": "El Pistolero",
                "resposta_oculta": "luis suarez",
                "clubes": ["Nacional", "Groningen", "Ajax", "Liverpool", "Barcelona", "Atlético de Madrid", "Nacional", "Grêmio", "Inter Miami"]
            },
            {
                "titulo": "O Último Melhor do Mundo do BR",
                "resposta_oculta": "kaka",
                "clubes": ["São Paulo", "Milan", "Real Madrid", "Milan", "São Paulo", "Orlando City"]
            },
            {
                "titulo": "O Monstro da Zaga",
                "resposta_oculta": "thiago silva",
                "clubes": ["RS Futebol", "Juventude", "Porto", "Dynamo Moscow", "Fluminense", "Milan", "PSG", "Chelsea", "Fluminense"]
            },
            {
                "titulo": "O Camisa 10 Esquecido",
                "resposta_oculta": "rivaldo",
                "clubes": ["Santa Cruz", "Mogi Mirim", "Corinthians", "Palmeiras", "Deportivo La Coruña", "Barcelona", "Milan", "Cruzeiro", "Olympiacos", "AEK", "Bunyodkor", "São Paulo", "Kabuscorp", "São Caetano", "Mogi Mirim"]
            },
            {
                "titulo": "O Cão de Guarda (Pitbull)",
                "resposta_oculta": "felipe melo",
                "clubes": ["Flamengo", "Cruzeiro", "Grêmio", "Mallorca", "Racing Santander", "Almería", "Fiorentina", "Juventus", "Galatasaray", "Inter de Milão", "Palmeiras", "Fluminense"]
            },
            {
                "titulo": "O Maestro Rodado",
                "resposta_oculta": "diego ribas",
                "clubes": ["Santos", "Porto", "Werder Bremen", "Juventus", "Wolfsburg", "Atlético de Madrid", "Fenerbahçe", "Flamengo"]
            },
            {
                "titulo": "O Francês Polêmico",
                "resposta_oculta": "anelka",
                "clubes": ["PSG", "Arsenal", "Real Madrid", "PSG", "Liverpool", "Manchester City", "Fenerbahçe", "Bolton", "Chelsea", "Shanghai Shenhua", "Juventus", "West Bromwich", "Mumbai City"]
            },
            {
                "titulo": "O Galáctico Inglês",
                "resposta_oculta": "david beckham",
                "clubes": ["Preston North End", "Manchester United", "Real Madrid", "LA Galaxy", "Milan", "PSG"]
            },
            {
                "titulo": "O Menino da Vila",
                "resposta_oculta": "neymar",
                "clubes": ["Santos", "Barcelona", "PSG", "Al-Hilal"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Mega Lote 9...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # Usa o índice (ordem) para garantir que no front-end eles apareçam
                # na exata posição: 0=Goleiro, 1..4=Defesa, 5..7=Meio, 8..10=Ataque
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" processado.'))

        # 2. PROCESSAR TRAJETÓRIAS E POPULAR CLUBES
        for dados in trajetorias:
            categoria, _ = CategoriaDesafio.objects.get_or_create(
                titulo=dados["titulo"], 
                tipo='trajetoria', 
                resposta_oculta=dados["resposta_oculta"]
            )
            for indice, nome_clube in enumerate(dados["clubes"]):
                clube_obj, _ = Clube.objects.get_or_create(nome=nome_clube)
                
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    clube_vinculado=clube_obj,
                    ordem=indice + 1
                )
            
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" processada.'))

        self.stdout.write(self.style.WARNING("\nMega Lote 9 Finalizado! Mais uma enxurrada de lendas na base de dados!"))

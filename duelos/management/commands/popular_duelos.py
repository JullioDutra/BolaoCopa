from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 15: Reis do Continente e Lendas Modernas'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 15 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Bayern de Munique 2019/20 (O Máquina do 8x2)",
                "jogadores": [
                    {"nome": "Neuer", "posicao": "Goleiro"}, 
                    {"nome": "Pavard", "posicao": "Lateral Direito"},
                    {"nome": "Boateng", "posicao": "Zagueiro"}, 
                    {"nome": "Alaba", "posicao": "Zagueiro"},
                    {"nome": "Alphonso Davies", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Kimmich", "posicao": "Volante"},
                    {"nome": "Goretzka", "posicao": "Volante"}, 
                    {"nome": "Thomas Müller", "posicao": "Meia-Atacante"},
                    {"nome": "Gnabry", "posicao": "Ponta Direita"}, 
                    {"nome": "Coman", "posicao": "Ponta Esquerda"},
                    {"nome": "Lewandowski", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Palmeiras 2021 (Bicampeão da América)",
                "jogadores": [
                    {"nome": "Weverton", "posicao": "Goleiro"}, 
                    {"nome": "Marcos Rocha", "posicao": "Lateral Direito"},
                    {"nome": "Luan", "posicao": "Zagueiro"}, 
                    {"nome": "Gustavo Gómez", "posicao": "Zagueiro"},
                    {"nome": "Piquerez", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Danilo", "posicao": "Volante"},
                    {"nome": "Zé Rafael", "posicao": "Volante"}, 
                    {"nome": "Raphael Veiga", "posicao": "Meia-Atacante"},
                    {"nome": "Dudu", "posicao": "Ponta Direita"}, 
                    {"nome": "Gustavo Scarpa", "posicao": "Ponta Esquerda"},
                    {"nome": "Rony", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Vasco 1997 (O Tri Brasileiro)",
                "jogadores": [
                    {"nome": "Carlos Germano", "posicao": "Goleiro"}, 
                    {"nome": "Válber", "posicao": "Lateral Direito"},
                    {"nome": "Odvan", "posicao": "Zagueiro"}, 
                    {"nome": "Mauro Galvão", "posicao": "Zagueiro"},
                    {"nome": "Felipe", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Luisinho", "posicao": "Volante"},
                    {"nome": "Nasa", "posicao": "Volante"}, 
                    {"nome": "Juninho Pernambucano", "posicao": "Meia-Atacante"},
                    {"nome": "Pedrinho", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Evair", "posicao": "Segundo Atacante"},
                    {"nome": "Edmundo", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Atlético Mineiro 2021 (O Ano Mágico)",
                "jogadores": [
                    {"nome": "Everson", "posicao": "Goleiro"}, 
                    {"nome": "Mariano", "posicao": "Lateral Direito"},
                    {"nome": "Nathan Silva", "posicao": "Zagueiro"}, 
                    {"nome": "Junior Alonso", "posicao": "Zagueiro"},
                    {"nome": "Guilherme Arana", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Allan", "posicao": "Volante"},
                    {"nome": "Jair", "posicao": "Volante"}, 
                    {"nome": "Zaracho", "posicao": "Meia Central"},
                    {"nome": "Nacho Fernández", "posicao": "Meia-Atacante"}, 
                    {"nome": "Keno", "posicao": "Ponta Esquerda"},
                    {"nome": "Hulk", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Cruzeiro 2014 (O Tetra Soberano)",
                "jogadores": [
                    {"nome": "Fábio", "posicao": "Goleiro"}, 
                    {"nome": "Mayke", "posicao": "Lateral Direito"},
                    {"nome": "Dedé", "posicao": "Zagueiro"}, 
                    {"nome": "Léo", "posicao": "Zagueiro"},
                    {"nome": "Egídio", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Lucas Silva", "posicao": "Volante"},
                    {"nome": "Henrique", "posicao": "Volante"}, 
                    {"nome": "Éverton Ribeiro", "posicao": "Meia-Atacante"},
                    {"nome": "Ricardo Goulart", "posicao": "Segundo Atacante"}, 
                    {"nome": "Willian Bigode", "posicao": "Ponta Esquerda"},
                    {"nome": "Marcelo Moreno", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Corinthians 2017 (A Quarta Força)",
                "jogadores": [
                    {"nome": "Cássio", "posicao": "Goleiro"}, 
                    {"nome": "Fagner", "posicao": "Lateral Direito"},
                    {"nome": "Balbuena", "posicao": "Zagueiro"}, 
                    {"nome": "Pablo", "posicao": "Zagueiro"},
                    {"nome": "Guilherme Arana", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Gabriel", "posicao": "Volante"},
                    {"nome": "Maycon", "posicao": "Volante"}, 
                    {"nome": "Rodriguinho", "posicao": "Meia Central"},
                    {"nome": "Jadson", "posicao": "Meia-Atacante"}, 
                    {"nome": "Romero", "posicao": "Ponta Esquerda"},
                    {"nome": "Jô", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "River Plate 2015 (A Primeira de Gallardo)",
                "jogadores": [
                    {"nome": "Barovero", "posicao": "Goleiro"}, 
                    {"nome": "Mercado", "posicao": "Lateral Direito"},
                    {"nome": "Maidana", "posicao": "Zagueiro"}, 
                    {"nome": "Funes Mori", "posicao": "Zagueiro"},
                    {"nome": "Vangioni", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Kranevitter", "posicao": "Volante"},
                    {"nome": "Ponzio", "posicao": "Volante"}, 
                    {"nome": "Carlos Sánchez", "posicao": "Meia Direita"},
                    {"nome": "Rodrigo Mora", "posicao": "Segundo Atacante"}, 
                    {"nome": "Driussi", "posicao": "Ponta Esquerda"},
                    {"nome": "Lucas Alario", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Milan 2002/03 (Os Campeões de Manchester)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, 
                    {"nome": "Simic", "posicao": "Lateral Direito"},
                    {"nome": "Nesta", "posicao": "Zagueiro"}, 
                    {"nome": "Costacurta", "posicao": "Zagueiro"},
                    {"nome": "Maldini", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Gattuso", "posicao": "Volante"},
                    {"nome": "Pirlo", "posicao": "Volante"}, 
                    {"nome": "Seedorf", "posicao": "Meia Esquerda"},
                    {"nome": "Rui Costa", "posicao": "Meia-Atacante"}, 
                    {"nome": "Shevchenko", "posicao": "Segundo Atacante"},
                    {"nome": "Inzaghi", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "São Paulo 2007 (O Bi Consecutivo)",
                "jogadores": [
                    {"nome": "Rogério Ceni", "posicao": "Goleiro"}, 
                    {"nome": "Souza", "posicao": "Lateral Direito"},
                    {"nome": "Breno", "posicao": "Zagueiro"}, 
                    {"nome": "Miranda", "posicao": "Zagueiro"},
                    {"nome": "Richarlyson", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Josué", "posicao": "Volante"},
                    {"nome": "Hernanes", "posicao": "Volante"}, 
                    {"nome": "Jorge Wagner", "posicao": "Meia Esquerda"},
                    {"nome": "Leandro", "posicao": "Ponta Direita"}, 
                    {"nome": "Dagoberto", "posicao": "Segundo Atacante"},
                    {"nome": "Borges", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 15 (LENDAS MODERNAS)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Rasta da Lateral",
                "resposta_oculta": "marcelo",
                "clubes": ["Fluminense", "Real Madrid", "Olympiacos", "Fluminense"]
            },
            {
                "titulo": "O Motorzinho Vencedor",
                "resposta_oculta": "casemiro",
                "clubes": ["São Paulo", "Real Madrid", "Porto", "Real Madrid", "Manchester United"]
            },
            {
                "titulo": "O Príncipe da Nação",
                "resposta_oculta": "gabigol",
                "clubes": ["Santos", "Inter de Milão", "Benfica", "Santos", "Flamengo"]
            },
            {
                "titulo": "O Miteiro",
                "resposta_oculta": "everton ribeiro",
                "clubes": ["Corinthians", "São Caetano", "Coritiba", "Cruzeiro", "Al Ahli", "Flamengo", "Bahia"]
            },
            {
                "titulo": "O Snowboarder Tricolor",
                "resposta_oculta": "thiago neves",
                "clubes": ["Paraná", "Fluminense", "Hamburgo", "Fluminense", "Al-Hilal", "Flamengo", "Fluminense", "Al-Jazira", "Cruzeiro", "Grêmio", "Sport"]
            },
            {
                "titulo": "El Cabezón",
                "resposta_oculta": "dalessandro",
                "clubes": ["River Plate", "Wolfsburg", "Portsmouth", "Zaragoza", "San Lorenzo", "Internacional", "River Plate", "Nacional", "Internacional"]
            },
            {
                "titulo": "O Ervilha do Gol",
                "resposta_oculta": "chicharito hernandez",
                "clubes": ["Guadalajara", "Manchester United", "Real Madrid", "Bayer Leverkusen", "West Ham", "Sevilla", "LA Galaxy", "Guadalajara"]
            },
            {
                "titulo": "O Charmoso Artilheiro",
                "resposta_oculta": "olivier giroud",
                "clubes": ["Grenoble", "Istres", "Tours", "Montpellier", "Arsenal", "Chelsea", "Milan", "Los Angeles FC"]
            },
            {
                "titulo": "O Rabo de Cavalo Divino",
                "resposta_oculta": "roberto baggio",
                "clubes": ["Vicenza", "Fiorentina", "Juventus", "Milan", "Bologna", "Inter de Milão", "Brescia"]
            },
            {
                "titulo": "Aquele que Corta pra Esquerda",
                "resposta_oculta": "arjen robben",
                "clubes": ["Groningen", "PSV", "Chelsea", "Real Madrid", "Bayern de Munique", "Groningen"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 15...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # A ordem (0=GK, 1-4=DEF, 5-7=MID, 8-10=ATT) garante que o campinho CSS não se desmonte
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" processado com Tática 4-3-3.'))

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
            
            # Adiciona os figurões da trajetória ao Autocomplete do sistema
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" habilitada.'))

        self.stdout.write(self.style.WARNING("\nLote 15 entregue com sucesso! Mais pedreiras prontas pro X1!"))

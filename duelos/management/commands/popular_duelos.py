from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 13: A Máquina do Tempo e os Viajantes da Bola'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 13 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Palmeiras 1993/94 (A Era Parmalat)",
                "jogadores": [
                    {"nome": "Velloso", "posicao": "Goleiro"}, 
                    {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Antônio Carlos", "posicao": "Zagueiro"}, 
                    {"nome": "Cléber", "posicao": "Zagueiro"},
                    {"nome": "Roberto Carlos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "César Sampaio", "posicao": "Volante"},
                    {"nome": "Mazinho", "posicao": "Volante"}, 
                    {"nome": "Zinho", "posicao": "Meia Central"},
                    {"nome": "Edílson", "posicao": "Ponta Direita"}, 
                    {"nome": "Edmundo", "posicao": "Ponta Esquerda"},
                    {"nome": "Evair", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Grêmio 1995 (Bicampeão da América)",
                "jogadores": [
                    {"nome": "Danrlei", "posicao": "Goleiro"}, 
                    {"nome": "Arce", "posicao": "Lateral Direito"},
                    {"nome": "Rivarola", "posicao": "Zagueiro"}, 
                    {"nome": "Adilson Batista", "posicao": "Zagueiro"},
                    {"nome": "Roger Machado", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Dinho", "posicao": "Volante"},
                    {"nome": "Luis Carlos Goiano", "posicao": "Volante"}, 
                    {"nome": "Carlos Miguel", "posicao": "Meia Central"},
                    {"nome": "Arilson", "posicao": "Meia-Atacante"}, 
                    {"nome": "Paulo Nunes", "posicao": "Segundo Atacante"},
                    {"nome": "Jardel", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Corinthians 1999 (Bicampeão Brasileiro)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, 
                    {"nome": "Índio", "posicao": "Lateral Direito"},
                    {"nome": "João Carlos", "posicao": "Zagueiro"}, 
                    {"nome": "Márcio Costa", "posicao": "Zagueiro"},
                    {"nome": "Kléber", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Vampeta", "posicao": "Volante"},
                    {"nome": "Rincón", "posicao": "Volante"}, 
                    {"nome": "Ricardinho", "posicao": "Meia Central"},
                    {"nome": "Marcelinho Carioca", "posicao": "Meia-Atacante"}, 
                    {"nome": "Edílson", "posicao": "Segundo Atacante"},
                    {"nome": "Luizão", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "França 2018 (Bicampeã do Mundo)",
                "jogadores": [
                    {"nome": "Lloris", "posicao": "Goleiro"}, 
                    {"nome": "Pavard", "posicao": "Lateral Direito"},
                    {"nome": "Varane", "posicao": "Zagueiro"}, 
                    {"nome": "Umtiti", "posicao": "Zagueiro"},
                    {"nome": "Lucas Hernandez", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Kanté", "posicao": "Volante"},
                    {"nome": "Pogba", "posicao": "Meia Central"}, 
                    {"nome": "Matuidi", "posicao": "Meia Esquerda"},
                    {"nome": "Mbappé", "posicao": "Ponta Direita"}, 
                    {"nome": "Griezmann", "posicao": "Segundo Atacante"},
                    {"nome": "Giroud", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Manchester City 2017/18 (Os Centurions)",
                "jogadores": [
                    {"nome": "Ederson", "posicao": "Goleiro"}, 
                    {"nome": "Kyle Walker", "posicao": "Lateral Direito"},
                    {"nome": "Kompany", "posicao": "Zagueiro"}, 
                    {"nome": "Otamendi", "posicao": "Zagueiro"},
                    {"nome": "Fabian Delph", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Fernandinho", "posicao": "Volante"},
                    {"nome": "Kevin De Bruyne", "posicao": "Meia Central"}, 
                    {"nome": "David Silva", "posicao": "Meia-Atacante"},
                    {"nome": "Raheem Sterling", "posicao": "Ponta Direita"}, 
                    {"nome": "Leroy Sané", "posicao": "Ponta Esquerda"},
                    {"nome": "Agüero", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Milan 1989/90 (O Esquadrão Imortal)",
                "jogadores": [
                    {"nome": "Giovanni Galli", "posicao": "Goleiro"}, 
                    {"nome": "Tassotti", "posicao": "Lateral Direito"},
                    {"nome": "Franco Baresi", "posicao": "Zagueiro"}, 
                    {"nome": "Costacurta", "posicao": "Zagueiro"},
                    {"nome": "Paolo Maldini", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Frank Rijkaard", "posicao": "Volante"},
                    {"nome": "Carlo Ancelotti", "posicao": "Meia Central"}, 
                    {"nome": "Donadoni", "posicao": "Meia Direita"},
                    {"nome": "Ruud Gullit", "posicao": "Meia-Atacante"}, 
                    {"nome": "Daniele Massaro", "posicao": "Segundo Atacante"},
                    {"nome": "Van Basten", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Holanda 1974 (O Carrossel Holandês)",
                "jogadores": [
                    {"nome": "Jongbloed", "posicao": "Goleiro"}, 
                    {"nome": "Suurbier", "posicao": "Lateral Direito"},
                    {"nome": "Rijsbergen", "posicao": "Zagueiro"}, 
                    {"nome": "Arie Haan", "posicao": "Zagueiro"},
                    {"nome": "Ruud Krol", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Wim Jansen", "posicao": "Volante"},
                    {"nome": "Johan Neeskens", "posicao": "Meia Central"}, 
                    {"nome": "Van Hanegem", "posicao": "Meia Esquerda"},
                    {"nome": "Johnny Rep", "posicao": "Ponta Direita"}, 
                    {"nome": "Rensenbrink", "posicao": "Ponta Esquerda"},
                    {"nome": "Johan Cruyff", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Real Madrid 2016/17 (A Duodécima)",
                "jogadores": [
                    {"nome": "Keylor Navas", "posicao": "Goleiro"}, 
                    {"nome": "Carvajal", "posicao": "Lateral Direito"},
                    {"nome": "Varane", "posicao": "Zagueiro"}, 
                    {"nome": "Sergio Ramos", "posicao": "Zagueiro"},
                    {"nome": "Marcelo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Casemiro", "posicao": "Volante"},
                    {"nome": "Toni Kroos", "posicao": "Meia Central"}, 
                    {"nome": "Luka Modric", "posicao": "Meia-Atacante"},
                    {"nome": "Gareth Bale", "posicao": "Ponta Direita"}, 
                    {"nome": "Cristiano Ronaldo", "posicao": "Ponta Esquerda"},
                    {"nome": "Benzema", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Athletico Paranaense 2018 (Campeão Sul-Americana)",
                "jogadores": [
                    {"nome": "Santos", "posicao": "Goleiro"}, 
                    {"nome": "Jonathan", "posicao": "Lateral Direito"},
                    {"nome": "Thiago Heleno", "posicao": "Zagueiro"}, 
                    {"nome": "Léo Pereira", "posicao": "Zagueiro"},
                    {"nome": "Renan Lodi", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Wellington", "posicao": "Volante"},
                    {"nome": "Bruno Guimarães", "posicao": "Meia Central"}, 
                    {"nome": "Lucho González", "posicao": "Meia-Atacante"},
                    {"nome": "Nikão", "posicao": "Ponta Direita"}, 
                    {"nome": "Marcelo Cirino", "posicao": "Ponta Esquerda"},
                    {"nome": "Pablo", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 13 (VIAJANTES DA BOLA)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Camisa 10 Colombiano",
                "resposta_oculta": "james rodriguez",
                "clubes": ["Envigado", "Banfield", "Porto", "Monaco", "Real Madrid", "Bayern de Munique", "Everton", "Al-Rayyan", "Olympiacos", "São Paulo"]
            },
            {
                "titulo": "O Zagueiro de Cabelos Enrolados",
                "resposta_oculta": "david luiz",
                "clubes": ["Vitória", "Benfica", "Chelsea", "PSG", "Chelsea", "Arsenal", "Flamengo"]
            },
            {
                "titulo": "O Gênio Cabeção",
                "resposta_oculta": "alex",
                "clubes": ["Coritiba", "Palmeiras", "Flamengo", "Cruzeiro", "Parma", "Cruzeiro", "Fenerbahçe", "Coritiba"]
            },
            {
                "titulo": "O Capitão do Penta",
                "resposta_oculta": "cafu",
                "clubes": ["São Paulo", "Zaragoza", "Juventude", "Palmeiras", "Roma", "Milan"]
            },
            {
                "titulo": "O Herói do Wolfsburg",
                "resposta_oculta": "grafite",
                "clubes": ["Matonense", "Ferroviária", "Santa Cruz", "Grêmio", "São Paulo", "Le Mans", "Wolfsburg", "Al Ahli", "Al-Sadd", "Santa Cruz"]
            },
            {
                "titulo": "O Rei de Itaquera",
                "resposta_oculta": "renato augusto",
                "clubes": ["Flamengo", "Bayer Leverkusen", "Corinthians", "Beijing Guoan", "Corinthians", "Fluminense"]
            },
            {
                "titulo": "O Lateral Inquieto",
                "resposta_oculta": "joao cancelo",
                "clubes": ["Benfica", "Valencia", "Inter de Milão", "Juventus", "Manchester City", "Bayern de Munique", "Barcelona"]
            },
            {
                "titulo": "O Pirata",
                "resposta_oculta": "hernan barcos",
                "clubes": ["Racing", "Guaraní", "LDU", "Palmeiras", "Grêmio", "Tianjin Teda", "Sporting", "Vélez Sarsfield", "Cruzeiro", "Alianza Lima"]
            },
            {
                "titulo": "O Cubo Mágico Suíço",
                "resposta_oculta": "xherdan shaqiri",
                "clubes": ["Basel", "Bayern de Munique", "Inter de Milão", "Stoke City", "Liverpool", "Lyon", "Chicago Fire"]
            },
            {
                "titulo": "O Maestro de Vidro",
                "resposta_oculta": "thiago alcantara",
                "clubes": ["Barcelona", "Bayern de Munique", "Liverpool"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 13...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # A ordem do array garante o encaixe perfeito na Tática 4-3-3 visual do front-end
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" processado com maestria.'))

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
            
            # Manda o nome oculto pro banco de autocomplete também
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" engatilhada.'))

        self.stdout.write(self.style.WARNING("\nLote 13 no ar! A sua base de dados já tem o peso de uma taça do Mundo!"))

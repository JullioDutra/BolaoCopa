from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 16: A Última Dança e os Ídolos Eternos'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 16 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "São Paulo 2012 (O Título Invicto)",
                "jogadores": [
                    {"nome": "Rogério Ceni", "posicao": "Goleiro"}, 
                    {"nome": "Paulo Miranda", "posicao": "Lateral Direito"},
                    {"nome": "Rafael Tolói", "posicao": "Zagueiro"}, 
                    {"nome": "Rhodolfo", "posicao": "Zagueiro"},
                    {"nome": "Cortez", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Wellington", "posicao": "Volante"},
                    {"nome": "Denilson", "posicao": "Volante"}, 
                    {"nome": "Jadson", "posicao": "Meia-Atacante"},
                    {"nome": "Lucas Moura", "posicao": "Ponta Direita"}, 
                    {"nome": "Osvaldo", "posicao": "Ponta Esquerda"},
                    {"nome": "Willian José", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Fluminense 1984 (O Casal 20)",
                "jogadores": [
                    {"nome": "Paulo Vítor", "posicao": "Goleiro"}, 
                    {"nome": "Aldo", "posicao": "Lateral Direito"},
                    {"nome": "Duílio", "posicao": "Zagueiro"}, 
                    {"nome": "Ricardo Gomes", "posicao": "Zagueiro"},
                    {"nome": "Branco", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Jandir", "posicao": "Volante"},
                    {"nome": "Deley", "posicao": "Meia Central"}, 
                    {"nome": "Assis", "posicao": "Meia-Atacante"},
                    {"nome": "Romerito", "posicao": "Ponta Direita"}, 
                    {"nome": "Tato", "posicao": "Ponta Esquerda"},
                    {"nome": "Washington", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Cruzeiro 1997 (Bicampeão da América)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, 
                    {"nome": "Vítor", "posicao": "Lateral Direito"},
                    {"nome": "Gélson Baresi", "posicao": "Zagueiro"}, 
                    {"nome": "Wilson Gottardo", "posicao": "Zagueiro"},
                    {"nome": "Nonato", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Fabinho", "posicao": "Volante"},
                    {"nome": "Ricardinho", "posicao": "Volante"}, 
                    {"nome": "Palhinha", "posicao": "Meia-Atacante"},
                    {"nome": "Elivélton", "posicao": "Ponta Direita"}, 
                    {"nome": "Cleisson", "posicao": "Ponta Esquerda"},
                    {"nome": "Marcelo Ramos", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Atlético Mineiro 2014 (Rei das Viradas)",
                "jogadores": [
                    {"nome": "Victor", "posicao": "Goleiro"}, 
                    {"nome": "Marcos Rocha", "posicao": "Lateral Direito"},
                    {"nome": "Jemerson", "posicao": "Zagueiro"}, 
                    {"nome": "Leonardo Silva", "posicao": "Zagueiro"},
                    {"nome": "Douglas Santos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Leandro Donizete", "posicao": "Volante"},
                    {"nome": "Rafael Carioca", "posicao": "Volante"}, 
                    {"nome": "Dátolo", "posicao": "Meia-Atacante"},
                    {"nome": "Luan", "posicao": "Ponta Direita"}, 
                    {"nome": "Diego Tardelli", "posicao": "Ponta Esquerda"},
                    {"nome": "Carlos", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Bayer Leverkusen 2001/02 (O Esquadrão do Quase)",
                "jogadores": [
                    {"nome": "Hans-Jörg Butt", "posicao": "Goleiro"}, 
                    {"nome": "Zoltán Sebescen", "posicao": "Lateral Direito"},
                    {"nome": "Lúcio", "posicao": "Zagueiro"}, 
                    {"nome": "Boris Zivkovic", "posicao": "Zagueiro"},
                    {"nome": "Diego Placente", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Carsten Ramelow", "posicao": "Volante"},
                    {"nome": "Michael Ballack", "posicao": "Meia Central"}, 
                    {"nome": "Yildiray Bastürk", "posicao": "Meia-Atacante"},
                    {"nome": "Bernd Schneider", "posicao": "Ponta Direita"}, 
                    {"nome": "Zé Roberto", "posicao": "Ponta Esquerda"},
                    {"nome": "Oliver Neuville", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Olympique de Marseille 1992/93 (Reis da Europa)",
                "jogadores": [
                    {"nome": "Fabien Barthez", "posicao": "Goleiro"}, 
                    {"nome": "Jocelyn Angloma", "posicao": "Lateral Direito"},
                    {"nome": "Basile Boli", "posicao": "Zagueiro"}, 
                    {"nome": "Marcel Desailly", "posicao": "Zagueiro"},
                    {"nome": "Éric Di Meco", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Didier Deschamps", "posicao": "Volante"},
                    {"nome": "Franck Sauzée", "posicao": "Meia Central"}, 
                    {"nome": "Jean-Jacques Eydelie", "posicao": "Meia-Atacante"},
                    {"nome": "Abedi Pelé", "posicao": "Ponta Direita"}, 
                    {"nome": "Alen Boksic", "posicao": "Ponta Esquerda"},
                    {"nome": "Rudi Völler", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Vasco 1989 (O Bi Brasileiro)",
                "jogadores": [
                    {"nome": "Acácio", "posicao": "Goleiro"}, 
                    {"nome": "Luiz Carlos Winck", "posicao": "Lateral Direito"},
                    {"nome": "Quiñónez", "posicao": "Zagueiro"}, 
                    {"nome": "Marco Aurélio", "posicao": "Zagueiro"},
                    {"nome": "Mazinho", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Zé do Carmo", "posicao": "Volante"},
                    {"nome": "Boiadeiro", "posicao": "Volante"}, 
                    {"nome": "Bismarck", "posicao": "Meia-Atacante"},
                    {"nome": "Sorato", "posicao": "Ponta Direita"}, 
                    {"nome": "William", "posicao": "Ponta Esquerda"},
                    {"nome": "Bebeto", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Borussia Dortmund 1996/97 (A Glória de Munique)",
                "jogadores": [
                    {"nome": "Stefan Klos", "posicao": "Goleiro"}, 
                    {"nome": "Stefan Reuter", "posicao": "Lateral Direito"},
                    {"nome": "Matthias Sammer", "posicao": "Zagueiro"}, 
                    {"nome": "Jürgen Kohler", "posicao": "Zagueiro"},
                    {"nome": "Jörg Heinrich", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Paul Lambert", "posicao": "Volante"},
                    {"nome": "Paulo Sousa", "posicao": "Meia Central"}, 
                    {"nome": "Andreas Möller", "posicao": "Meia-Atacante"},
                    {"nome": "Karl-Heinz Riedle", "posicao": "Ponta Direita"}, 
                    {"nome": "Stéphane Chapuisat", "posicao": "Ponta Esquerda"},
                    {"nome": "Lars Ricken", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Porto 1986/87 (O Calcanhar de Madjer)",
                "jogadores": [
                    {"nome": "Józef Mlynarczyk", "posicao": "Goleiro"}, 
                    {"nome": "João Pinto", "posicao": "Lateral Direito"},
                    {"nome": "Celso", "posicao": "Zagueiro"}, 
                    {"nome": "Eduardo Luís", "posicao": "Zagueiro"},
                    {"nome": "Augusto Inácio", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Quim", "posicao": "Volante"},
                    {"nome": "António André", "posicao": "Volante"}, 
                    {"nome": "Jaime Magalhães", "posicao": "Meia-Atacante"},
                    {"nome": "Rabah Madjer", "posicao": "Ponta Direita"}, 
                    {"nome": "Paulo Futre", "posicao": "Ponta Esquerda"},
                    {"nome": "Fernando Gomes", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 16 (A ÚLTIMA DANÇA)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Fabuloso",
                "resposta_oculta": "luis fabiano",
                "clubes": ["Ponte Preta", "Rennes", "São Paulo", "Porto", "Sevilla", "São Paulo", "Tianjin Quanjian", "Vasco"]
            },
            {
                "titulo": "O Rei dos Gols (e dos Stories)",
                "resposta_oculta": "fred",
                "clubes": ["América-MG", "Cruzeiro", "Lyon", "Fluminense", "Atlético Mineiro", "Cruzeiro", "Fluminense"]
            },
            {
                "titulo": "O Volante Artilheiro",
                "resposta_oculta": "paulinho",
                "clubes": ["Pão de Açúcar", "Bragantino", "Corinthians", "Tottenham", "Guangzhou Evergrande", "Barcelona", "Guangzhou FC", "Al-Ahli", "Corinthians"]
            },
            {
                "titulo": "O Imperador do Gol",
                "resposta_oculta": "julio cesar",
                "clubes": ["Flamengo", "Chievo", "Inter de Milão", "QPR", "Toronto FC", "Benfica", "Flamengo"]
            },
            {
                "titulo": "O Último Camisa 10 Clássico",
                "resposta_oculta": "riquelme",
                "clubes": ["Boca Juniors", "Barcelona", "Villarreal", "Boca Juniors", "Argentinos Juniors"]
            },
            {
                "titulo": "O Zagueiro Elegante",
                "resposta_oculta": "miranda",
                "clubes": ["Coritiba", "Sochaux", "São Paulo", "Atlético de Madrid", "Inter de Milão", "Jiangsu Suning", "São Paulo"]
            },
            {
                "titulo": "O Herói do Maracanã",
                "resposta_oculta": "mario gotze",
                "clubes": ["Borussia Dortmund", "Bayern de Munique", "Borussia Dortmund", "PSV", "Eintracht Frankfurt"]
            },
            {
                "titulo": "O Velho Vamp",
                "resposta_oculta": "vampeta",
                "clubes": ["Vitória", "PSV", "VVV-Venlo", "Fluminense", "Corinthians", "Inter de Milão", "PSG", "Flamengo", "Corinthians", "Brasiliense", "Goiás"]
            },
            {
                "titulo": "O Sucessor",
                "resposta_oculta": "nani",
                "clubes": ["Sporting", "Manchester United", "Sporting", "Fenerbahçe", "Valencia", "Lazio", "Sporting", "Orlando City", "Venezia", "Melbourne Victory", "Adana Demirspor", "Estrela da Amadora"]
            },
            {
                "titulo": "O Volante de Vidro",
                "resposta_oculta": "fernando gago",
                "clubes": ["Boca Juniors", "Real Madrid", "Roma", "Valencia", "Vélez Sarsfield", "Boca Juniors", "Vélez Sarsfield"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 16 (A Saideira)...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # A ordem do array (0=GK, 1-4=DEF, 5-7=MID, 8-10=ATT) perfeitamente alinhada!
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" carimbado na prancheta.'))

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
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" finalizada.'))

        self.stdout.write(self.style.WARNING("\nLote 16 Concluído com Sucesso! O banco de dados agora é um verdadeiro MUSEU DO FUTEBOL! 🏟️🏆"))

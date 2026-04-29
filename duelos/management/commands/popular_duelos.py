from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 17 (O Lote Definitivo): Esquadrões de Ouro e Nômades'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 17 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Manchester United 1998/99 (A Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Peter Schmeichel", "posicao": "Goleiro"}, 
                    {"nome": "Gary Neville", "posicao": "Lateral Direito"},
                    {"nome": "Jaap Stam", "posicao": "Zagueiro"}, 
                    {"nome": "Ronny Johnsen", "posicao": "Zagueiro"},
                    {"nome": "Denis Irwin", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Roy Keane", "posicao": "Volante"},
                    {"nome": "Paul Scholes", "posicao": "Meia Central"}, 
                    {"nome": "David Beckham", "posicao": "Meia Direita"},
                    {"nome": "Ryan Giggs", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Dwight Yorke", "posicao": "Segundo Atacante"},
                    {"nome": "Andy Cole", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Palmeiras 1996 (A Máquina dos 100 Gols)",
                "jogadores": [
                    {"nome": "Velloso", "posicao": "Goleiro"}, 
                    {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Sandro Blum", "posicao": "Zagueiro"}, 
                    {"nome": "Cléber", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Galeano", "posicao": "Volante"},
                    {"nome": "Amaral", "posicao": "Volante"}, 
                    {"nome": "Djalminha", "posicao": "Meia-Atacante"},
                    {"nome": "Rivaldo", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Müller", "posicao": "Segundo Atacante"},
                    {"nome": "Luizão", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Barcelona 1991/92 (O Dream Team de Cruyff)",
                "jogadores": [
                    {"nome": "Zubizarreta", "posicao": "Goleiro"}, 
                    {"nome": "Albert Ferrer", "posicao": "Lateral Direito"},
                    {"nome": "Ronald Koeman", "posicao": "Zagueiro"}, 
                    {"nome": "Nando", "posicao": "Zagueiro"},
                    {"nome": "Juan Carlos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Pep Guardiola", "posicao": "Volante"},
                    {"nome": "Bakero", "posicao": "Meia Central"}, 
                    {"nome": "Michael Laudrup", "posicao": "Meia-Atacante"},
                    {"nome": "Eusebio", "posicao": "Ponta Direita"}, 
                    {"nome": "Stoichkov", "posicao": "Segundo Atacante"},
                    {"nome": "Julio Salinas", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "River Plate 1996 (Reis da América)",
                "jogadores": [
                    {"nome": "Germán Burgos", "posicao": "Goleiro"}, 
                    {"nome": "Hernán Díaz", "posicao": "Lateral Direito"},
                    {"nome": "Celso Ayala", "posicao": "Zagueiro"}, 
                    {"nome": "Rivarola", "posicao": "Zagueiro"},
                    {"nome": "Sorín", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Almeyda", "posicao": "Volante"},
                    {"nome": "Astrada", "posicao": "Volante"}, 
                    {"nome": "Gallardo", "posicao": "Meia-Atacante"},
                    {"nome": "Ariel Ortega", "posicao": "Ponta Direita"}, 
                    {"nome": "Enzo Francescoli", "posicao": "Segundo Atacante"},
                    {"nome": "Hernán Crespo", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Fluminense 2010 (O Tri Brasileiro)",
                "jogadores": [
                    {"nome": "Ricardo Berna", "posicao": "Goleiro"}, 
                    {"nome": "Mariano", "posicao": "Lateral Direito"},
                    {"nome": "Gum", "posicao": "Zagueiro"}, 
                    {"nome": "Leandro Euzébio", "posicao": "Zagueiro"},
                    {"nome": "Carlinhos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Diguinho", "posicao": "Volante"},
                    {"nome": "Valencia", "posicao": "Volante"}, 
                    {"nome": "Deco", "posicao": "Meia Central"},
                    {"nome": "Conca", "posicao": "Meia-Atacante"}, 
                    {"nome": "Emerson Sheik", "posicao": "Segundo Atacante"},
                    {"nome": "Fred", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Bahia 1988 (O Esquadrão de Aço Campeão)",
                "jogadores": [
                    {"nome": "Ronaldo", "posicao": "Goleiro"}, 
                    {"nome": "Tarantini", "posicao": "Lateral Direito"},
                    {"nome": "João Marcelo", "posicao": "Zagueiro"}, 
                    {"nome": "Claudir", "posicao": "Zagueiro"},
                    {"nome": "Paulo Robson", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Paulo Rodrigues", "posicao": "Volante"},
                    {"nome": "Gil Sergipano", "posicao": "Volante"}, 
                    {"nome": "Bobô", "posicao": "Meia-Atacante"},
                    {"nome": "Zé Carlos", "posicao": "Ponta Direita"}, 
                    {"nome": "Marquinhos", "posicao": "Ponta Esquerda"},
                    {"nome": "Charles Fabian", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Ajax 1971/72 (Futebol Total)",
                "jogadores": [
                    {"nome": "Heinz Stuy", "posicao": "Goleiro"}, 
                    {"nome": "Wim Suurbier", "posicao": "Lateral Direito"},
                    {"nome": "Barry Hulshoff", "posicao": "Zagueiro"}, 
                    {"nome": "Horst Blankenburg", "posicao": "Zagueiro"},
                    {"nome": "Ruud Krol", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Johan Neeskens", "posicao": "Volante"},
                    {"nome": "Arie Haan", "posicao": "Meia Central"}, 
                    {"nome": "Gerrie Mühren", "posicao": "Meia Esquerda"},
                    {"nome": "Sjaak Swart", "posicao": "Ponta Direita"}, 
                    {"nome": "Piet Keizer", "posicao": "Ponta Esquerda"},
                    {"nome": "Johan Cruyff", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Juventus 1984/85 (O Esquadrão de Platini)",
                "jogadores": [
                    {"nome": "Tacconi", "posicao": "Goleiro"}, 
                    {"nome": "Favero", "posicao": "Lateral Direito"},
                    {"nome": "Scirea", "posicao": "Zagueiro"}, 
                    {"nome": "Brio", "posicao": "Zagueiro"},
                    {"nome": "Cabrini", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Bonini", "posicao": "Volante"},
                    {"nome": "Tardelli", "posicao": "Meia Central"}, 
                    {"nome": "Michel Platini", "posicao": "Meia-Atacante"},
                    {"nome": "Briaschi", "posicao": "Ponta Direita"}, 
                    {"nome": "Boniek", "posicao": "Segundo Atacante"},
                    {"nome": "Paolo Rossi", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Real Madrid 1959/60 (Os Primeiros Galácticos)",
                "jogadores": [
                    {"nome": "Juan Alonso", "posicao": "Goleiro"}, 
                    {"nome": "Marquitos", "posicao": "Lateral Direito"},
                    {"nome": "Santamaría", "posicao": "Zagueiro"}, 
                    {"nome": "Lesmes", "posicao": "Zagueiro"},
                    {"nome": "Zárraga", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Miguel Muñoz", "posicao": "Volante"},
                    {"nome": "Kopa", "posicao": "Meia Direita"}, 
                    {"nome": "Rial", "posicao": "Meia Esquerda"},
                    {"nome": "Paco Gento", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Puskás", "posicao": "Segundo Atacante"},
                    {"nome": "Di Stéfano", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Benfica 1961/62 (A Lenda de Eusébio)",
                "jogadores": [
                    {"nome": "Costa Pereira", "posicao": "Goleiro"}, 
                    {"nome": "Mário João", "posicao": "Lateral Direito"},
                    {"nome": "Germano", "posicao": "Zagueiro"}, 
                    {"nome": "Fernando Cruz", "posicao": "Zagueiro"},
                    {"nome": "Ângelo Martins", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Cavém", "posicao": "Volante"},
                    {"nome": "Coluna", "posicao": "Meia Central"}, 
                    {"nome": "José Augusto", "posicao": "Meia Direita"},
                    {"nome": "Simões", "posicao": "Ponta Esquerda"}, 
                    {"nome": "José Águas", "posicao": "Centroavante"},
                    {"nome": "Eusébio", "posicao": "Segundo Atacante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 17 (NÔMADES E A SAIDEIRA)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Samurai Viajante",
                "resposta_oculta": "keisuke honda",
                "clubes": ["Nagoya Grampus", "VVV-Venlo", "CSKA Moscou", "Milan", "Pachuca", "Melbourne Victory", "Vitesse", "Botafogo", "Neftchi Baku", "Suduva"]
            },
            {
                "titulo": "El Mago",
                "resposta_oculta": "valdivia",
                "clubes": ["Colo-Colo", "Palmeiras", "Al Ain", "Palmeiras", "Al Wahda", "Colo-Colo", "Mazatlán", "Necaxa"]
            },
            {
                "titulo": "O Foguete Foguinho",
                "resposta_oculta": "willian",
                "clubes": ["Corinthians", "Shakhtar Donetsk", "Anzhi", "Chelsea", "Arsenal", "Corinthians", "Fulham", "Olympiacos"]
            },
            {
                "titulo": "O Leão do Meio Campo",
                "resposta_oculta": "luiz gustavo",
                "clubes": ["Corinthians Alagoano", "Hoffenheim", "Bayern de Munique", "Wolfsburg", "Marseille", "Fenerbahçe", "Al-Nassr", "São Paulo"]
            },
            {
                "titulo": "O Ídolo Improvável do Galo",
                "resposta_oculta": "diego tardelli",
                "clubes": ["São Paulo", "Betis", "São Caetano", "PSV", "Atlético Mineiro", "Anzhi", "Al-Gharafa", "Atlético Mineiro", "Shandong Luneng", "Grêmio", "Atlético Mineiro", "Santos"]
            },
            {
                "titulo": "O Matador Tricolor",
                "resposta_oculta": "rafael sobis",
                "clubes": ["Internacional", "Betis", "Al-Jazira", "Internacional", "Fluminense", "Tigres", "Cruzeiro", "Internacional", "Ceará", "Cruzeiro"]
            },
            {
                "titulo": "O Pantera",
                "resposta_oculta": "bafetimbi gomis",
                "clubes": ["Saint-Étienne", "Lyon", "Swansea", "Marseille", "Galatasaray", "Al-Hilal", "Galatasaray", "Kawasaki Frontale"]
            },
            {
                "titulo": "O Dono da Lateral (e da Dança)",
                "resposta_oculta": "juan cuadrado",
                "clubes": ["Independiente Medellín", "Udinese", "Lecce", "Fiorentina", "Chelsea", "Juventus", "Inter de Milão", "Atalanta"]
            },
            {
                "titulo": "O Menino de Ouro Belga",
                "resposta_oculta": "eden hazard",
                "clubes": ["Lille", "Chelsea", "Real Madrid"]
            },
            {
                "titulo": "O Bad Boy Francês",
                "resposta_oculta": "hatem ben arfa",
                "clubes": ["Lyon", "Marseille", "Newcastle", "Hull City", "Nice", "PSG", "Rennes", "Valladolid", "Bordeaux", "Lille"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 17 (O Definitivo)...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # O índice perfeito para encaixar no seu layout 4-3-3 (Goleiro = 0 / Defensores = 1-4 / Meias = 5-7 / Atacantes = 8-10)
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Esquadrão "{dados["titulo"]}" escalado na prancheta!'))

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
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" engatilhada!'))

        self.stdout.write(self.style.WARNING("\nLote 17 - A Saideira Suprema concluída! A base de dados do Cartolândia virou um monumento ao futebol mundial! 🏆🔥"))

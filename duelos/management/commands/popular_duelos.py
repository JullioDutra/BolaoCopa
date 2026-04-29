from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 8: Mega Lote de Esquadrões Históricos e Lendas do Futebol'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 8 (ESQUADRÕES INESQUECÍVEIS)
        # ==========================================
        elencos = [
            {
                "titulo": "São Paulo 2005 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Rogério Ceni", "posicao": "Goleiro"}, 
                    {"nome": "Cicinho", "posicao": "Lateral Direito"},
                    {"nome": "Lugano", "posicao": "Zagueiro"}, 
                    {"nome": "Fabão", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Mineiro", "posicao": "Volante"},
                    {"nome": "Josué", "posicao": "Volante"}, 
                    {"nome": "Danilo", "posicao": "Meia Central"},
                    {"nome": "Luizão", "posicao": "Centroavante"}, 
                    {"nome": "Amoroso", "posicao": "Atacante"},
                    {"nome": "Aloísio", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Santos 2011 (Tri da Libertadores)",
                "jogadores": [
                    {"nome": "Rafael", "posicao": "Goleiro"}, 
                    {"nome": "Danilo", "posicao": "Lateral Direito"},
                    {"nome": "Edu Dracena", "posicao": "Zagueiro"}, 
                    {"nome": "Durval", "posicao": "Zagueiro"},
                    {"nome": "Léo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Arouca", "posicao": "Volante"},
                    {"nome": "Henrique", "posicao": "Volante"}, 
                    {"nome": "Elano", "posicao": "Meia"},
                    {"nome": "Ganso", "posicao": "Meia-Atacante"}, 
                    {"nome": "Neymar", "posicao": "Ponta Esquerda"},
                    {"nome": "Zé Eduardo", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Barcelona 2008/09 (O Sextete)",
                "jogadores": [
                    {"nome": "Víctor Valdés", "posicao": "Goleiro"}, 
                    {"nome": "Dani Alves", "posicao": "Lateral Direito"},
                    {"nome": "Puyol", "posicao": "Zagueiro"}, 
                    {"nome": "Piqué", "posicao": "Zagueiro"},
                    {"nome": "Abidal", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Yaya Touré", "posicao": "Volante"},
                    {"nome": "Xavi", "posicao": "Meia Central"}, 
                    {"nome": "Iniesta", "posicao": "Meia Central"},
                    {"nome": "Messi", "posicao": "Ponta Direita"}, 
                    {"nome": "Thierry Henry", "posicao": "Ponta Esquerda"},
                    {"nome": "Eto'o", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Cruzeiro 2003 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Gomes", "posicao": "Goleiro"}, 
                    {"nome": "Maurinho", "posicao": "Lateral Direito"},
                    {"nome": "Cris", "posicao": "Zagueiro"}, 
                    {"nome": "Edu Dracena", "posicao": "Zagueiro"},
                    {"nome": "Leandro", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Augusto Recife", "posicao": "Volante"},
                    {"nome": "Maldonado", "posicao": "Volante"}, 
                    {"nome": "Wendell", "posicao": "Meia"},
                    {"nome": "Alex", "posicao": "Meia-Atacante"}, 
                    {"nome": "Aristizábal", "posicao": "Centroavante"},
                    {"nome": "Mota", "posicao": "Atacante"}
                ]
            },
            {
                "titulo": "Real Madrid 2013/14 (La Décima)",
                "jogadores": [
                    {"nome": "Casillas", "posicao": "Goleiro"}, 
                    {"nome": "Carvajal", "posicao": "Lateral Direito"},
                    {"nome": "Sergio Ramos", "posicao": "Zagueiro"}, 
                    {"nome": "Pepe", "posicao": "Zagueiro"},
                    {"nome": "Marcelo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Xabi Alonso", "posicao": "Volante"},
                    {"nome": "Modric", "posicao": "Meia Central"}, 
                    {"nome": "Di María", "posicao": "Meia"},
                    {"nome": "Gareth Bale", "posicao": "Ponta Direita"}, 
                    {"nome": "Cristiano Ronaldo", "posicao": "Ponta Esquerda"},
                    {"nome": "Benzema", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Internacional 2006 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Clemer", "posicao": "Goleiro"}, 
                    {"nome": "Ceará", "posicao": "Lateral Direito"},
                    {"nome": "Índio", "posicao": "Zagueiro"}, 
                    {"nome": "Fabiano Eller", "posicao": "Zagueiro"},
                    {"nome": "Rubens Cardoso", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Edinho", "posicao": "Volante"},
                    {"nome": "Wellington Monteiro", "posicao": "Volante"}, 
                    {"nome": "Alex", "posicao": "Meia"},
                    {"nome": "Fernandão", "posicao": "Meia-Atacante"}, 
                    {"nome": "Iarley", "posicao": "Segundo Atacante"},
                    {"nome": "Alexandre Pato", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Bayern de Munique 2012/13 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Neuer", "posicao": "Goleiro"}, 
                    {"nome": "Lahm", "posicao": "Lateral Direito"},
                    {"nome": "Boateng", "posicao": "Zagueiro"}, 
                    {"nome": "Dante", "posicao": "Zagueiro"},
                    {"nome": "Alaba", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Javi Martínez", "posicao": "Volante"},
                    {"nome": "Schweinsteiger", "posicao": "Meia Central"}, 
                    {"nome": "Thomas Müller", "posicao": "Meia-Atacante"},
                    {"nome": "Robben", "posicao": "Ponta Direita"}, 
                    {"nome": "Ribéry", "posicao": "Ponta Esquerda"},
                    {"nome": "Mandzukic", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Grêmio 2017 (Tri da Libertadores)",
                "jogadores": [
                    {"nome": "Marcelo Grohe", "posicao": "Goleiro"}, 
                    {"nome": "Edílson", "posicao": "Lateral Direito"},
                    {"nome": "Geromel", "posicao": "Zagueiro"}, 
                    {"nome": "Kannemann", "posicao": "Zagueiro"},
                    {"nome": "Cortez", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Michel", "posicao": "Volante"},
                    {"nome": "Arthur", "posicao": "Volante"}, 
                    {"nome": "Ramiro", "posicao": "Meia Direita"},
                    {"nome": "Luan", "posicao": "Meia-Atacante"}, 
                    {"nome": "Fernandinho", "posicao": "Ponta Esquerda"},
                    {"nome": "Lucas Barrios", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Ajax 1994/95 (Campeão Invicto Champions)",
                "jogadores": [
                    {"nome": "Van der Sar", "posicao": "Goleiro"}, 
                    {"nome": "Reiziger", "posicao": "Lateral Direito"},
                    {"nome": "Blind", "posicao": "Zagueiro"}, 
                    {"nome": "Frank de Boer", "posicao": "Zagueiro"},
                    {"nome": "Rijkaard", "posicao": "Volante"}, 
                    {"nome": "Seedorf", "posicao": "Meia Direita"},
                    {"nome": "Edgar Davids", "posicao": "Meia Esquerda"}, 
                    {"nome": "Litmanen", "posicao": "Meia-Atacante"},
                    {"nome": "Finidi George", "posicao": "Ponta Direita"}, 
                    {"nome": "Overmars", "posicao": "Ponta Esquerda"},
                    {"nome": "Ronald de Boer", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 8 (LENDAS GLOBAIS)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Fenômeno",
                "resposta_oculta": "ronaldo",
                "clubes": ["Cruzeiro", "PSV", "Barcelona", "Inter de Milão", "Real Madrid", "Milan", "Corinthians"]
            },
            {
                "titulo": "O Bruxo",
                "resposta_oculta": "ronaldinho",
                "clubes": ["Grêmio", "PSG", "Barcelona", "Milan", "Flamengo", "Atlético Mineiro", "Querétaro", "Fluminense"]
            },
            {
                "titulo": "O Imperador",
                "resposta_oculta": "adriano",
                "clubes": ["Flamengo", "Inter de Milão", "Fiorentina", "Parma", "Inter de Milão", "São Paulo", "Inter de Milão", "Flamengo", "Roma", "Corinthians", "Athletico Paranaense"]
            },
            {
                "titulo": "Deus Zlatan",
                "resposta_oculta": "ibrahimovic",
                "clubes": ["Malmö", "Ajax", "Juventus", "Inter de Milão", "Barcelona", "Milan", "PSG", "Manchester United", "LA Galaxy", "Milan"]
            },
            {
                "titulo": "O Baixinho",
                "resposta_oculta": "romario",
                "clubes": ["Vasco", "PSV", "Barcelona", "Flamengo", "Valencia", "Flamengo", "Vasco", "Fluminense", "Al-Sadd", "Vasco", "Miami FC", "América-RJ"]
            },
            {
                "titulo": "O Maestro Francês",
                "resposta_oculta": "zidane",
                "clubes": ["Cannes", "Bordeaux", "Juventus", "Real Madrid"]
            },
            {
                "titulo": "A Lenda Camaronesa",
                "resposta_oculta": "etoo",
                "clubes": ["Real Madrid", "Leganés", "Espanyol", "Mallorca", "Barcelona", "Inter de Milão", "Anzhi", "Chelsea", "Everton", "Sampdoria", "Antalyaspor", "Qatar SC"]
            },
            {
                "titulo": "Rei da África",
                "resposta_oculta": "drogba",
                "clubes": ["Le Mans", "Guingamp", "Marseille", "Chelsea", "Shanghai Shenhua", "Galatasaray", "Chelsea", "Montreal Impact", "Phoenix Rising"]
            },
            {
                "titulo": "Motorzinho Argentino",
                "resposta_oculta": "di maria",
                "clubes": ["Rosario Central", "Benfica", "Real Madrid", "Manchester United", "PSG", "Juventus", "Benfica"]
            },
            {
                "titulo": "O Professor Holandês",
                "resposta_oculta": "seedorf",
                "clubes": ["Ajax", "Sampdoria", "Real Madrid", "Inter de Milão", "Milan", "Botafogo"]
            },
            {
                "titulo": "Batigol",
                "resposta_oculta": "batistuta",
                "clubes": ["Newell's Old Boys", "River Plate", "Boca Juniors", "Fiorentina", "Roma", "Inter de Milão", "Al-Arabi"]
            },
            {
                "titulo": "O Polivalente",
                "resposta_oculta": "vidal",
                "clubes": ["Colo-Colo", "Bayer Leverkusen", "Juventus", "Bayern de Munique", "Barcelona", "Inter de Milão", "Flamengo", "Athletico Paranaense", "Colo-Colo"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Mega Lote 8...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for j in dados["jogadores"]:
                # Garante que o jogador vai pro banco do autocomplete
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=0
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
                # Garante que o clube existe para podermos associar o escudo depois
                clube_obj, _ = Clube.objects.get_or_create(nome=nome_clube)
                
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    clube_vinculado=clube_obj,
                    ordem=indice + 1
                )
            
            # Adiciona o nome oculto da trajetória ao banco de jogadores também (para autocomplete)
            # Capitalizando o nome para ficar bonito no banco
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" processada.'))

        self.stdout.write(self.style.WARNING("\nMega Lote 8 Finalizado com Sucesso! Seu banco de dados está gigante!"))

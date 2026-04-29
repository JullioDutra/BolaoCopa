from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 11: Os Galácticos e as Zebras Históricas'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 11 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Alemanha 2014 (O Pesadelo do 7x1)",
                "jogadores": [
                    {"nome": "Neuer", "posicao": "Goleiro"}, 
                    {"nome": "Lahm", "posicao": "Lateral Direito"},
                    {"nome": "Boateng", "posicao": "Zagueiro"}, 
                    {"nome": "Hummels", "posicao": "Zagueiro"},
                    {"nome": "Höwedes", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Schweinsteiger", "posicao": "Volante"},
                    {"nome": "Khedira", "posicao": "Volante"}, 
                    {"nome": "Toni Kroos", "posicao": "Meia Central"},
                    {"nome": "Thomas Müller", "posicao": "Ponta Direita"}, 
                    {"nome": "Özil", "posicao": "Ponta Esquerda"},
                    {"nome": "Klose", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Fluminense 2023 (Donos da América)",
                "jogadores": [
                    {"nome": "Fábio", "posicao": "Goleiro"}, 
                    {"nome": "Samuel Xavier", "posicao": "Lateral Direito"},
                    {"nome": "Nino", "posicao": "Zagueiro"}, 
                    {"nome": "Felipe Melo", "posicao": "Zagueiro"},
                    {"nome": "Marcelo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "André", "posicao": "Volante"},
                    {"nome": "Martinelli", "posicao": "Volante"}, 
                    {"nome": "Ganso", "posicao": "Meia-Atacante"},
                    {"nome": "Jhon Arias", "posicao": "Ponta Direita"}, 
                    {"nome": "Keno", "posicao": "Ponta Esquerda"},
                    {"nome": "Germán Cano", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Corinthians 2000 (O 1º Mundial)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, 
                    {"nome": "Índio", "posicao": "Lateral Direito"},
                    {"nome": "Fábio Luciano", "posicao": "Zagueiro"}, 
                    {"nome": "Adilson", "posicao": "Zagueiro"},
                    {"nome": "Kleber", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Vampeta", "posicao": "Volante"},
                    {"nome": "Rincón", "posicao": "Volante"}, 
                    {"nome": "Ricardinho", "posicao": "Meia Central"},
                    {"nome": "Marcelinho Carioca", "posicao": "Ponta Direita"}, 
                    {"nome": "Edílson", "posicao": "Segundo Atacante"},
                    {"nome": "Luizão", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Leicester City 2015/16 (O Milagre da Premier)",
                "jogadores": [
                    {"nome": "Kasper Schmeichel", "posicao": "Goleiro"}, 
                    {"nome": "Danny Simpson", "posicao": "Lateral Direito"},
                    {"nome": "Wes Morgan", "posicao": "Zagueiro"}, 
                    {"nome": "Robert Huth", "posicao": "Zagueiro"},
                    {"nome": "Christian Fuchs", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "N'Golo Kanté", "posicao": "Volante"},
                    {"nome": "Danny Drinkwater", "posicao": "Volante"}, 
                    {"nome": "Riyad Mahrez", "posicao": "Meia Direita"},
                    {"nome": "Marc Albrighton", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Shinji Okazaki", "posicao": "Segundo Atacante"},
                    {"nome": "Jamie Vardy", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "São Paulo 1992 (O 1º Mundial de Telê)",
                "jogadores": [
                    {"nome": "Zetti", "posicao": "Goleiro"}, 
                    {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Adilson", "posicao": "Zagueiro"}, 
                    {"nome": "Ronaldão", "posicao": "Zagueiro"},
                    {"nome": "Ronaldo Luiz", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Pintado", "posicao": "Volante"},
                    {"nome": "Toninho Cerezo", "posicao": "Volante"}, 
                    {"nome": "Raí", "posicao": "Meia-Atacante"},
                    {"nome": "Elivélton", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Müller", "posicao": "Segundo Atacante"},
                    {"nome": "Palhinha", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Itália 2006 (O Tetra em Berlim)",
                "jogadores": [
                    {"nome": "Buffon", "posicao": "Goleiro"}, 
                    {"nome": "Zambrotta", "posicao": "Lateral Direito"},
                    {"nome": "Cannavaro", "posicao": "Zagueiro"}, 
                    {"nome": "Materazzi", "posicao": "Zagueiro"},
                    {"nome": "Grosso", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Gattuso", "posicao": "Volante"},
                    {"nome": "Pirlo", "posicao": "Volante"}, 
                    {"nome": "Camoranesi", "posicao": "Meia Direita"},
                    {"nome": "Totti", "posicao": "Meia-Atacante"}, 
                    {"nome": "Del Piero", "posicao": "Segundo Atacante"},
                    {"nome": "Luca Toni", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Real Madrid 2001/02 (O Voleio de Zidane)",
                "jogadores": [
                    {"nome": "César", "posicao": "Goleiro"}, 
                    {"nome": "Michel Salgado", "posicao": "Lateral Direito"},
                    {"nome": "Hierro", "posicao": "Zagueiro"}, 
                    {"nome": "Helguera", "posicao": "Zagueiro"},
                    {"nome": "Roberto Carlos", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Makelele", "posicao": "Volante"},
                    {"nome": "Luís Figo", "posicao": "Meia Direita"}, 
                    {"nome": "Zidane", "posicao": "Meia-Atacante"},
                    {"nome": "Solari", "posicao": "Ponta Esquerda"}, 
                    {"nome": "Raúl", "posicao": "Segundo Atacante"},
                    {"nome": "Morientes", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Atlético de Madrid 2013/14 (El Cholo)",
                "jogadores": [
                    {"nome": "Courtois", "posicao": "Goleiro"}, 
                    {"nome": "Juanfran", "posicao": "Lateral Direito"},
                    {"nome": "Miranda", "posicao": "Zagueiro"}, 
                    {"nome": "Godín", "posicao": "Zagueiro"},
                    {"nome": "Filipe Luís", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Gabi", "posicao": "Volante"},
                    {"nome": "Tiago", "posicao": "Volante"}, 
                    {"nome": "Koke", "posicao": "Meia Esquerda"},
                    {"nome": "Arda Turan", "posicao": "Ponta Direita"}, 
                    {"nome": "Raúl García", "posicao": "Segundo Atacante"},
                    {"nome": "Diego Costa", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Santos 1962 (O Esquadrão de Pelé)",
                "jogadores": [
                    {"nome": "Gilmar", "posicao": "Goleiro"}, 
                    {"nome": "Lima", "posicao": "Lateral Direito"},
                    {"nome": "Mauro Ramos", "posicao": "Zagueiro"}, 
                    {"nome": "Calvet", "posicao": "Zagueiro"},
                    {"nome": "Dalmo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Zito", "posicao": "Volante"},
                    {"nome": "Mengálvio", "posicao": "Meia Central"}, 
                    {"nome": "Pelé", "posicao": "Meia-Atacante"},
                    {"nome": "Dorval", "posicao": "Ponta Direita"}, 
                    {"nome": "Pepe", "posicao": "Ponta Esquerda"},
                    {"nome": "Coutinho", "posicao": "Centroavante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 11 (CRAQUES MUNDIAIS)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Expresso Galês",
                "resposta_oculta": "gareth bale",
                "clubes": ["Southampton", "Tottenham", "Real Madrid", "Tottenham", "Los Angeles FC"]
            },
            {
                "titulo": "O Pequeno Mágico",
                "resposta_oculta": "philippe coutinho",
                "clubes": ["Vasco", "Inter de Milão", "Espanyol", "Liverpool", "Barcelona", "Bayern de Munique", "Aston Villa", "Al-Duhail", "Vasco"]
            },
            {
                "titulo": "El Niño",
                "resposta_oculta": "fernando torres",
                "clubes": ["Atlético de Madrid", "Liverpool", "Chelsea", "Milan", "Atlético de Madrid", "Sagan Tosu"]
            },
            {
                "titulo": "O Tanque Belga",
                "resposta_oculta": "romelu lukaku",
                "clubes": ["Anderlecht", "Chelsea", "West Bromwich", "Everton", "Manchester United", "Inter de Milão", "Chelsea", "Inter de Milão", "Roma", "Napoli"]
            },
            {
                "titulo": "El Jefecito (O Chefinho)",
                "resposta_oculta": "javier mascherano",
                "clubes": ["River Plate", "Corinthians", "West Ham", "Liverpool", "Barcelona", "Hebei China Fortune", "Estudiantes"]
            },
            {
                "titulo": "Kun",
                "resposta_oculta": "sergio aguero",
                "clubes": ["Independiente", "Atlético de Madrid", "Manchester City", "Barcelona"]
            },
            {
                "titulo": "O Garçom Alemão",
                "resposta_oculta": "mesut ozil",
                "clubes": ["Schalke 04", "Werder Bremen", "Real Madrid", "Arsenal", "Fenerbahçe", "Istanbul Basaksehir"]
            },
            {
                "titulo": "O Traidor de Madrid",
                "resposta_oculta": "luis figo",
                "clubes": ["Sporting", "Barcelona", "Real Madrid", "Inter de Milão"]
            },
            {
                "titulo": "O Ídolo do Chelsea",
                "resposta_oculta": "frank lampard",
                "clubes": ["West Ham", "Swansea", "Chelsea", "Manchester City", "New York City FC"]
            },
            {
                "titulo": "O Artilheiro que Tinha Medo de Voar",
                "resposta_oculta": "dennis bergkamp",
                "clubes": ["Ajax", "Inter de Milão", "Arsenal"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 11...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # Respeitando a ordem do array (0=Goleiro, 1..4=Defesa, 5..7=Meio, 8..10=Ataque)
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
            
            # Adiciona o dono da trajetória ao autocomplete
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" processada.'))

        self.stdout.write(self.style.WARNING("\nLote 11 Finalizado! A resenha tá cada vez mais pesada e o banco de dados tá voando! 🚀⚽"))

from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Adiciona o Lote 14: Reis de Copas e Andarilhos da Bola'

    def handle(self, *args, **kwargs):
        # ==========================================
        # ELENCOS - LOTE 14 (ORDEM 4-3-3 EXATA PARA O FRONTEND)
        # 1 Goleiro | 4 Defesa | 3 Meio | 3 Ataque
        # ==========================================
        elencos = [
            {
                "titulo": "Brasil 1994 (O Tetra nos EUA)",
                "jogadores": [
                    {"nome": "Taffarel", "posicao": "Goleiro"}, 
                    {"nome": "Jorginho", "posicao": "Lateral Direito"},
                    {"nome": "Aldair", "posicao": "Zagueiro"}, 
                    {"nome": "Márcio Santos", "posicao": "Zagueiro"},
                    {"nome": "Branco", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Mauro Silva", "posicao": "Volante"},
                    {"nome": "Dunga", "posicao": "Volante"}, 
                    {"nome": "Mazinho", "posicao": "Meia Central"},
                    {"nome": "Zinho", "posicao": "Meia Esquerda"}, 
                    {"nome": "Bebeto", "posicao": "Segundo Atacante"},
                    {"nome": "Romário", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Barcelona 2014/15 (O Trio MSN)",
                "jogadores": [
                    {"nome": "Ter Stegen", "posicao": "Goleiro"}, 
                    {"nome": "Dani Alves", "posicao": "Lateral Direito"},
                    {"nome": "Piqué", "posicao": "Zagueiro"}, 
                    {"nome": "Mascherano", "posicao": "Zagueiro"},
                    {"nome": "Jordi Alba", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Busquets", "posicao": "Volante"},
                    {"nome": "Rakitic", "posicao": "Meia Central"}, 
                    {"nome": "Iniesta", "posicao": "Meia-Atacante"},
                    {"nome": "Messi", "posicao": "Ponta Direita"}, 
                    {"nome": "Neymar", "posicao": "Ponta Esquerda"},
                    {"nome": "Luis Suárez", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Flamengo 2009 (O Hexa Brasileiro)",
                "jogadores": [
                    {"nome": "Bruno", "posicao": "Goleiro"}, 
                    {"nome": "Léo Moura", "posicao": "Lateral Direito"},
                    {"nome": "Álvaro", "posicao": "Zagueiro"}, 
                    {"nome": "Ronaldo Angelim", "posicao": "Zagueiro"},
                    {"nome": "Juan", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Airton", "posicao": "Volante"},
                    {"nome": "Willians", "posicao": "Volante"}, 
                    {"nome": "Petkovic", "posicao": "Meia-Atacante"},
                    {"nome": "Zé Roberto", "posicao": "Meia Direita"}, 
                    {"nome": "Emerson Sheik", "posicao": "Segundo Atacante"},
                    {"nome": "Adriano", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Santos 2002 (Os Meninos da Vila)",
                "jogadores": [
                    {"nome": "Fábio Costa", "posicao": "Goleiro"}, 
                    {"nome": "Maurinho", "posicao": "Lateral Direito"},
                    {"nome": "Alex", "posicao": "Zagueiro"}, 
                    {"nome": "Preto", "posicao": "Zagueiro"},
                    {"nome": "Léo", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Paulo Almeida", "posicao": "Volante"},
                    {"nome": "Renato", "posicao": "Volante"}, 
                    {"nome": "Diego", "posicao": "Meia-Atacante"},
                    {"nome": "Elano", "posicao": "Ponta Direita"}, 
                    {"nome": "Robinho", "posicao": "Ponta Esquerda"},
                    {"nome": "Alberto", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Chelsea 2011/12 (Milagre de Munique)",
                "jogadores": [
                    {"nome": "Petr Cech", "posicao": "Goleiro"}, 
                    {"nome": "Bosingwa", "posicao": "Lateral Direito"},
                    {"nome": "David Luiz", "posicao": "Zagueiro"}, 
                    {"nome": "Gary Cahill", "posicao": "Zagueiro"},
                    {"nome": "Ashley Cole", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Mikel", "posicao": "Volante"},
                    {"nome": "Ramires", "posicao": "Meia Central"}, 
                    {"nome": "Frank Lampard", "posicao": "Meia-Atacante"},
                    {"nome": "Salomon Kalou", "posicao": "Ponta Direita"}, 
                    {"nome": "Juan Mata", "posicao": "Ponta Esquerda"},
                    {"nome": "Drogba", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Grêmio 1983 (Mundial de Clubes)",
                "jogadores": [
                    {"nome": "Mazaropi", "posicao": "Goleiro"}, 
                    {"nome": "Paulo Roberto", "posicao": "Lateral Direito"},
                    {"nome": "Baidek", "posicao": "Zagueiro"}, 
                    {"nome": "De León", "posicao": "Zagueiro"},
                    {"nome": "Paulo César", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "China", "posicao": "Volante"},
                    {"nome": "Osvaldo", "posicao": "Meia Central"}, 
                    {"nome": "Tita", "posicao": "Meia-Atacante"},
                    {"nome": "Renato Gaúcho", "posicao": "Ponta Direita"}, 
                    {"nome": "Mário Sérgio", "posicao": "Ponta Esquerda"},
                    {"nome": "Tarciso", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Corinthians 1990 (O 1º Brasileirão)",
                "jogadores": [
                    {"nome": "Ronaldo Giovanelli", "posicao": "Goleiro"}, 
                    {"nome": "Giba", "posicao": "Lateral Direito"},
                    {"nome": "Marcelo Djian", "posicao": "Zagueiro"}, 
                    {"nome": "Guinei", "posicao": "Zagueiro"},
                    {"nome": "Jacenir", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Márcio", "posicao": "Volante"},
                    {"nome": "Wilson Mano", "posicao": "Volante"}, 
                    {"nome": "Neto", "posicao": "Meia-Atacante"},
                    {"nome": "Fabinho", "posicao": "Ponta Direita"}, 
                    {"nome": "Tupãzinho", "posicao": "Segundo Atacante"},
                    {"nome": "Paulo Sérgio", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Fluminense 2008 (Vice da Libertadores)",
                "jogadores": [
                    {"nome": "Fernando Henrique", "posicao": "Goleiro"}, 
                    {"nome": "Gabriel", "posicao": "Lateral Direito"},
                    {"nome": "Thiago Silva", "posicao": "Zagueiro"}, 
                    {"nome": "Luiz Alberto", "posicao": "Zagueiro"},
                    {"nome": "Junior Cesar", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Ygor", "posicao": "Volante"},
                    {"nome": "Arouca", "posicao": "Volante"}, 
                    {"nome": "Conca", "posicao": "Meia-Atacante"},
                    {"nome": "Thiago Neves", "posicao": "Meia Esquerda"}, 
                    {"nome": "Dodô", "posicao": "Segundo Atacante"},
                    {"nome": "Washington", "posicao": "Centroavante"}
                ]
            },
            {
                "titulo": "Napoli 1989/90 (O Scudetto de D10S)",
                "jogadores": [
                    {"nome": "Giuliani", "posicao": "Goleiro"}, 
                    {"nome": "Ferrara", "posicao": "Lateral Direito"},
                    {"nome": "Baroni", "posicao": "Zagueiro"}, 
                    {"nome": "Corradini", "posicao": "Zagueiro"},
                    {"nome": "Francini", "posicao": "Lateral Esquerdo"}, 
                    {"nome": "Alemao", "posicao": "Volante"},
                    {"nome": "De Napoli", "posicao": "Meia Central"}, 
                    {"nome": "Crippa", "posicao": "Meia Direita"},
                    {"nome": "Maradona", "posicao": "Meia-Atacante"}, 
                    {"nome": "Careca", "posicao": "Centroavante"},
                    {"nome": "Carnevale", "posicao": "Segundo Atacante"}
                ]
            }
        ]

        # ==========================================
        # TRAJETÓRIAS - LOTE 14 (OS ANDARILHOS DA BOLA)
        # ==========================================
        trajetorias = [
            {
                "titulo": "O Tanque dos Pulos",
                "resposta_oculta": "diego souza",
                "clubes": ["Fluminense", "Flamengo", "Benfica", "Grêmio", "Palmeiras", "Atlético Mineiro", "Vasco", "Cruzeiro", "Metalist", "Sport", "São Paulo", "Botafogo"]
            },
            {
                "titulo": "O Cabeludo da Lateral",
                "resposta_oculta": "juan pablo sorin",
                "clubes": ["Argentinos Juniors", "Juventus", "River Plate", "Cruzeiro", "Lazio", "Barcelona", "PSG", "Villarreal", "Cruzeiro"]
            },
            {
                "titulo": "O Pitbull de Óculos",
                "resposta_oculta": "edgar davids",
                "clubes": ["Ajax", "Milan", "Juventus", "Barcelona", "Inter de Milão", "Tottenham", "Crystal Palace"]
            },
            {
                "titulo": "O Maestro Espanhol",
                "resposta_oculta": "cesc fabregas",
                "clubes": ["Arsenal", "Barcelona", "Chelsea", "Monaco", "Como"]
            },
            {
                "titulo": "La Brujita",
                "resposta_oculta": "juan sebastian veron",
                "clubes": ["Estudiantes", "Boca Juniors", "Sampdoria", "Parma", "Lazio", "Manchester United", "Chelsea", "Inter de Milão", "Estudiantes"]
            },
            {
                "titulo": "O Camisa 10 Marrento",
                "resposta_oculta": "djalminha",
                "clubes": ["Flamengo", "Guarani", "Palmeiras", "Deportivo La Coruña", "Austria Wien", "América-MG"]
            },
            {
                "titulo": "O Holandês Matador",
                "resposta_oculta": "patrick kluivert",
                "clubes": ["Ajax", "Milan", "Barcelona", "Newcastle", "Valencia", "PSV", "Lille"]
            },
            {
                "titulo": "O General do Meio Campo",
                "resposta_oculta": "gennaro gattuso",
                "clubes": ["Perugia", "Rangers", "Salernitana", "Milan", "Sion"]
            },
            {
                "titulo": "O Rei do 'Embala Nenem'",
                "resposta_oculta": "bebeto",
                "clubes": ["Vitória", "Flamengo", "Vasco", "Deportivo La Coruña", "Sevilla", "Botafogo", "Kashima Antlers", "Vasco"]
            },
            {
                "titulo": "O Maestro Lento",
                "resposta_oculta": "ganso",
                "clubes": ["Paysandu", "Santos", "São Paulo", "Sevilla", "Amiens", "Fluminense"]
            }
        ]

        self.stdout.write("Iniciando Povoamento do Lote 14...")

        # 1. PROCESSAR ELENCOS E POPULAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            for indice, j in enumerate(dados["jogadores"]):
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # A ordem garante que o 4-3-3 visual no front-end não quebre
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=indice
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{dados["titulo"]}" processado com sucesso.'))

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
            
            # Adiciona os donos das trajetórias ao autocomplete geral
            nome_jogador = dados["resposta_oculta"].title()
            JogadorBanco.objects.get_or_create(nome=nome_jogador)
            
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{dados["titulo"]}" registrada.'))

        self.stdout.write(self.style.WARNING("\nLote 14 Concluído! O servidor já deve estar pesando de tanta lenda junta! 🏆"))

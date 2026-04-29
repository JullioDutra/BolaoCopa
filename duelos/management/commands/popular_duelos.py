from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Povoa o banco de dados centralizado de Clubes, Jogadores e Desafios (Mega Lote)'

    def handle(self, *args, **kwargs):
        # ==========================================
        # TODOS OS ELENCOS
        # ==========================================
        elencos = [
            # --- LOTE 1 ---
            {
                "titulo": "Palmeiras 1999 (Libertadores)",
                "jogadores": [
                    {"nome": "Marcos", "posicao": "Goleiro"}, {"nome": "Arce", "posicao": "Lateral Direito"},
                    {"nome": "Júnior Baiano", "posicao": "Zagueiro"}, {"nome": "Roque Júnior", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"}, {"nome": "César Sampaio", "posicao": "Volante"},
                    {"nome": "Rogério", "posicao": "Volante"}, {"nome": "Zinho", "posicao": "Meia"},
                    {"nome": "Alex", "posicao": "Meia-Atacante"}, {"nome": "Paulo Nunes", "posicao": "Atacante"},
                    {"nome": "Oséas", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Milan 2005 (A Lenda Europeia)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"}, {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Stam", "posicao": "Zagueiro"}, {"nome": "Nesta", "posicao": "Zagueiro"},
                    {"nome": "Maldini", "posicao": "Lateral Esquerdo"}, {"nome": "Pirlo", "posicao": "Volante"},
                    {"nome": "Gattuso", "posicao": "Meia Central"}, {"nome": "Seedorf", "posicao": "Meia Esquerda"},
                    {"nome": "Kaká", "posicao": "Meia-Atacante"}, {"nome": "Shevchenko", "posicao": "Atacante"},
                    {"nome": "Crespo", "posicao": "Centroavante"},
                ]
            },
            # --- LOTE 2 ---
            {
                "titulo": "Real Madrid 2002/03 (Os Galácticos)",
                "jogadores": [
                    {"nome": "Casillas", "posicao": "Goleiro"}, {"nome": "Michel Salgado", "posicao": "Lateral Direito"},
                    {"nome": "Fernando Hierro", "posicao": "Zagueiro"}, {"nome": "Iván Helguera", "posicao": "Zagueiro"},
                    {"nome": "Roberto Carlos", "posicao": "Lateral Esquerdo"}, {"nome": "Claude Makélélé", "posicao": "Volante"},
                    {"nome": "Luís Figo", "posicao": "Meia Direita"}, {"nome": "Zinedine Zidane", "posicao": "Meia Central"},
                    {"nome": "Guti", "posicao": "Meia Esquerda"}, {"nome": "Raúl", "posicao": "Segundo Atacante"},
                    {"nome": "Ronaldo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Flamengo 2019 (A Máquina de Jesus)",
                "jogadores": [
                    {"nome": "Diego Alves", "posicao": "Goleiro"}, {"nome": "Rafinha", "posicao": "Lateral Direito"},
                    {"nome": "Rodrigo Caio", "posicao": "Zagueiro"}, {"nome": "Pablo Marí", "posicao": "Zagueiro"},
                    {"nome": "Filipe Luís", "posicao": "Lateral Esquerdo"}, {"nome": "Willian Arão", "posicao": "Volante"},
                    {"nome": "Gerson", "posicao": "Meia"}, {"nome": "Éverton Ribeiro", "posicao": "Meia Direita"},
                    {"nome": "De Arrascaeta", "posicao": "Meia Esquerda"}, {"nome": "Bruno Henrique", "posicao": "Atacante"},
                    {"nome": "Gabriel Barbosa", "posicao": "Centroavante"},
                ]
            },
            # --- LOTE 3 (NOVOS!) ---
            {
                "titulo": "Chelsea 2012 (Milagre de Munique)",
                "jogadores": [
                    {"nome": "Petr Cech", "posicao": "Goleiro"}, {"nome": "Bosingwa", "posicao": "Lateral Direito"},
                    {"nome": "David Luiz", "posicao": "Zagueiro"}, {"nome": "Gary Cahill", "posicao": "Zagueiro"},
                    {"nome": "Ashley Cole", "posicao": "Lateral Esquerdo"}, {"nome": "Mikel", "posicao": "Volante"},
                    {"nome": "Frank Lampard", "posicao": "Meia Central"}, {"nome": "Salomon Kalou", "posicao": "Ponta Direita"},
                    {"nome": "Juan Mata", "posicao": "Meia-Atacante"}, {"nome": "Ryan Bertrand", "posicao": "Ponta Esquerda"},
                    {"nome": "Didier Drogba", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Bayern de Munique 2013 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Manuel Neuer", "posicao": "Goleiro"}, {"nome": "Philipp Lahm", "posicao": "Lateral Direito"},
                    {"nome": "Jerome Boateng", "posicao": "Zagueiro"}, {"nome": "Dante", "posicao": "Zagueiro"},
                    {"nome": "David Alaba", "posicao": "Lateral Esquerdo"}, {"nome": "Javi Martínez", "posicao": "Volante"},
                    {"nome": "Schweinsteiger", "posicao": "Meia Central"}, {"nome": "Arjen Robben", "posicao": "Ponta Direita"},
                    {"nome": "Thomas Müller", "posicao": "Meia-Atacante"}, {"nome": "Franck Ribéry", "posicao": "Ponta Esquerda"},
                    {"nome": "Mario Mandzukic", "posicao": "Centroavante"},
                ]
            }
        ]

        # ==========================================
        # TODAS AS TRAJETÓRIAS
        # ==========================================
        trajetorias = [
            # --- LOTE 1 ---
            {
                "titulo": "Gênio Indomável",
                "resposta_oculta": "romario",
                "clubes": ["Vasco", "PSV", "Barcelona", "Flamengo", "Valencia", "Fluminense", "Al-Sadd", "Miami FC", "América-RJ"]
            },
            {
                "titulo": "O Canhão Imparável",
                "resposta_oculta": "roberto carlos",
                "clubes": ["União São João", "Palmeiras", "Inter de Milão", "Real Madrid", "Fenerbahçe", "Corinthians", "Anzhi", "Delhi Dynamos"]
            },
            # --- LOTE 2 ---
            {
                "titulo": "O Maior Peregrino",
                "resposta_oculta": "loco abreu",
                "clubes": ["Defensor Sporting", "San Lorenzo", "Deportivo La Coruña", "Nacional", "Cruz Azul", "Monterrey", "Botafogo", "Rosario Central", "Bangu"]
            },
            {
                "titulo": "Cachorro Louco Romeno",
                "resposta_oculta": "edgar davids",
                "clubes": ["Ajax", "Milan", "Juventus", "Barcelona", "Inter de Milão", "Tottenham", "Crystal Palace"]
            },
            # --- LOTE 3 (NOVOS!) ---
            {
                "titulo": "Rei da Trivela",
                "resposta_oculta": "quaresma",
                "clubes": ["Sporting", "Barcelona", "Porto", "Inter de Milão", "Chelsea", "Besiktas", "Al Ahli", "Kasımpaşa", "Vitória de Guimarães"]
            },
            {
                "titulo": "Artilheiro Alemão-Brasileiro",
                "resposta_oculta": "grafite",
                "clubes": ["Ferroviária", "Santa Cruz", "Grêmio", "Goiás", "São Paulo", "Le Mans", "Wolfsburg", "Al Ahli", "Athletico Paranaense"]
            },
            {
                "titulo": "Xerife de Portugal",
                "resposta_oculta": "pepe",
                "clubes": ["Marítimo", "Porto", "Real Madrid", "Besiktas", "Porto"]
            },
            {
                "titulo": "O Príncipe de Roma",
                "resposta_oculta": "totti",
                "clubes": ["Roma"] # Uma pequena armadilha para os mais rápidos!
            }
        ]

        self.stdout.write("Iniciando Povoamento Inteligente...\n")

        # 1. PROCESSAR ELENCOS E ALIMENTAR BANCO DE JOGADORES
        for dados in elencos:
            categoria, _ = CategoriaDesafio.objects.get_or_create(titulo=dados["titulo"], tipo='elenco')
            
            for j in dados["jogadores"]:
                # Cria o jogador no Banco Centralizado se não existir
                jogador_obj, _ = JogadorBanco.objects.get_or_create(nome=j["nome"])
                
                # Associa ao desafio
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    jogador_vinculado=jogador_obj,
                    posicao_tatica=j["posicao"],
                    ordem=0
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Elenco "{categoria.titulo}" e seus jogadores registados!'))

        # 2. PROCESSAR TRAJETÓRIAS E ALIMENTAR BANCO DE CLUBES
        for dados in trajetorias:
            categoria, _ = CategoriaDesafio.objects.get_or_create(
                titulo=dados["titulo"], 
                tipo='trajetoria', 
                resposta_oculta=dados["resposta_oculta"]
            )
            
            for indice, nome_clube in enumerate(dados["clubes"]):
                # Cria o clube no Banco Centralizado se não existir
                clube_obj, _ = Clube.objects.get_or_create(nome=nome_clube)
                
                # Associa ao desafio
                ItemDesafio.objects.get_or_create(
                    categoria=categoria,
                    clube_vinculado=clube_obj,
                    ordem=indice + 1
                )
            self.stdout.write(self.style.SUCCESS(f'[+] Trajetória "{categoria.titulo}" e seus clubes registados!'))

        self.stdout.write(self.style.SUCCESS("\nConcluído! Todos os bancos estão atualizados com o Mega Lote."))
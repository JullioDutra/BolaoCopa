from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Povoa o banco de dados centralizado de Clubes, Jogadores e Desafios'

    def handle(self, *args, **kwargs):
# ==========================================
        # 1. DADOS DOS ELENCOS (Campinho)
        # ==========================================
        elencos_lote_2 = [
            {
                "titulo": "Real Madrid 2002/03 (Os Galácticos)",
                "jogadores": [
                    {"nome": "Casillas", "posicao": "Goleiro"},
                    {"nome": "Michel Salgado", "posicao": "Lateral Direito"},
                    {"nome": "Fernando Hierro", "posicao": "Zagueiro"},
                    {"nome": "Iván Helguera", "posicao": "Zagueiro"},
                    {"nome": "Roberto Carlos", "posicao": "Lateral Esquerdo"},
                    {"nome": "Claude Makélélé", "posicao": "Volante"},
                    {"nome": "Luís Figo", "posicao": "Meia Direita"},
                    {"nome": "Zinedine Zidane", "posicao": "Meia Central"},
                    {"nome": "Guti", "posicao": "Meia Esquerda"},
                    {"nome": "Raúl", "posicao": "Segundo Atacante"},
                    {"nome": "Ronaldo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Fluminense 2012 (Tetra Brasileiro)",
                "jogadores": [
                    {"nome": "Diego Cavalieri", "posicao": "Goleiro"},
                    {"nome": "Bruno", "posicao": "Lateral Direito"},
                    {"nome": "Gum", "posicao": "Zagueiro"},
                    {"nome": "Leandro Euzébio", "posicao": "Zagueiro"},
                    {"nome": "Carlinhos", "posicao": "Lateral Esquerdo"},
                    {"nome": "Edinho", "posicao": "Volante"},
                    {"nome": "Jean", "posicao": "Volante"},
                    {"nome": "Deco", "posicao": "Meia"},
                    {"nome": "Thiago Neves", "posicao": "Meia-Atacante"},
                    {"nome": "Wellington Nem", "posicao": "Atacante"},
                    {"nome": "Fred", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Grêmio 2017 (Tri da Libertadores)",
                "jogadores": [
                    {"nome": "Marcelo Grohe", "posicao": "Goleiro"},
                    {"nome": "Edílson", "posicao": "Lateral Direito"},
                    {"nome": "Pedro Geromel", "posicao": "Zagueiro"},
                    {"nome": "Walter Kannemann", "posicao": "Zagueiro"},
                    {"nome": "Bruno Cortez", "posicao": "Lateral Esquerdo"},
                    {"nome": "Michel", "posicao": "Volante"},
                    {"nome": "Arthur", "posicao": "Volante"},
                    {"nome": "Ramiro", "posicao": "Meia Direita"},
                    {"nome": "Luan", "posicao": "Meia-Atacante"},
                    {"nome": "Fernandinho", "posicao": "Ponta Esquerda"},
                    {"nome": "Lucas Barrios", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Barcelona 2010/11 (Era Guardiola)",
                "jogadores": [
                    {"nome": "Víctor Valdés", "posicao": "Goleiro"},
                    {"nome": "Daniel Alves", "posicao": "Lateral Direito"},
                    {"nome": "Gerard Piqué", "posicao": "Zagueiro"},
                    {"nome": "Carles Puyol", "posicao": "Zagueiro"},
                    {"nome": "Éric Abidal", "posicao": "Lateral Esquerdo"},
                    {"nome": "Sergio Busquets", "posicao": "Volante"},
                    {"nome": "Xavi Hernández", "posicao": "Meia Central"},
                    {"nome": "Andrés Iniesta", "posicao": "Meia Central"},
                    {"nome": "Pedro", "posicao": "Ponta Direita"},
                    {"nome": "Lionel Messi", "posicao": "Falso 9"},
                    {"nome": "David Villa", "posicao": "Ponta Esquerda"},
                ]
            },
            {
                "titulo": "Boca Juniors 2007 (Libertadores)",
                "jogadores": [
                    {"nome": "Mauricio Caranta", "posicao": "Goleiro"},
                    {"nome": "Hugo Ibarra", "posicao": "Lateral Direito"},
                    {"nome": "Cata Díaz", "posicao": "Zagueiro"},
                    {"nome": "Claudio Morel", "posicao": "Zagueiro"},
                    {"nome": "Clemente Rodríguez", "posicao": "Lateral Esquerdo"},
                    {"nome": "Pablo Ledesma", "posicao": "Volante"},
                    {"nome": "Éver Banega", "posicao": "Volante"},
                    {"nome": "Neri Cardozo", "posicao": "Meia"},
                    {"nome": "Juan Román Riquelme", "posicao": "Meia-Atacante"},
                    {"nome": "Rodrigo Palacio", "posicao": "Atacante"},
                    {"nome": "Martín Palermo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Flamengo 2019 (A Máquina de Jesus)",
                "jogadores": [
                    {"nome": "Diego Alves", "posicao": "Goleiro"},
                    {"nome": "Rafinha", "posicao": "Lateral Direito"},
                    {"nome": "Rodrigo Caio", "posicao": "Zagueiro"},
                    {"nome": "Pablo Marí", "posicao": "Zagueiro"},
                    {"nome": "Filipe Luís", "posicao": "Lateral Esquerdo"},
                    {"nome": "Willian Arão", "posicao": "Volante"},
                    {"nome": "Gerson", "posicao": "Meia"},
                    {"nome": "Éverton Ribeiro", "posicao": "Meia Direita"},
                    {"nome": "De Arrascaeta", "posicao": "Meia Esquerda"},
                    {"nome": "Bruno Henrique", "posicao": "Atacante"},
                    {"nome": "Gabriel Barbosa", "posicao": "Centroavante"},
                ]
            }
        ]

        # ==========================================
        # 2. DADOS DAS TRAJETÓRIAS (Escudos)
        # ==========================================
        trajetorias_lote_2 = [
            {
                "titulo": "O Maior Peregrino",
                "resposta_oculta": "loco abreu",
                "clubes": ["Defensor Sporting", "San Lorenzo", "Deportivo La Coruña", "Nacional", "Cruz Azul", "Monterrey", "Botafogo", "Rosario Central", "Bangu"]
            },
            {
                "titulo": "Canhota Mágica do Penta",
                "resposta_oculta": "rivaldo",
                "clubes": ["Santa Cruz", "Mogi Mirim", "Corinthians", "Palmeiras", "Deportivo La Coruña", "Barcelona", "Milan", "Cruzeiro", "Olympiacos", "São Paulo"]
            },
            {
                "titulo": "Cachorro Louco Romeno",
                "resposta_oculta": "edgar davids",
                "clubes": ["Ajax", "Milan", "Juventus", "Barcelona", "Inter de Milão", "Tottenham", "Crystal Palace"]
            },
            {
                "titulo": "El Cabezón",
                "resposta_oculta": "d'alessandro",
                "clubes": ["River Plate", "Wolfsburg", "Portsmouth", "Zaragoza", "San Lorenzo", "Internacional", "Nacional"]
            },
            {
                "titulo": "Super Mario",
                "resposta_oculta": "mario balotelli",
                "clubes": ["Lumezzane", "Inter de Milão", "Manchester City", "Milan", "Liverpool", "Nice", "Olympique de Marseille", "Brescia"]
            },
            {
                "titulo": "Leão Indomável",
                "resposta_oculta": "samuel eto'o",
                "clubes": ["Real Madrid", "Mallorca", "Barcelona", "Inter de Milão", "Anzhi", "Chelsea", "Everton", "Sampdoria"]
            },
            {
                "titulo": "O Pirata",
                "resposta_oculta": "hernan barcos",
                "clubes": ["Racing", "Guaraní", "LDU", "Palmeiras", "Grêmio", "Sporting", "Vélez Sarsfield", "Cruzeiro", "Alianza Lima"]
            },
            {
                "titulo": "Cabeludo e Guerreiro",
                "resposta_oculta": "juan pablo sorin",
                "clubes": ["Argentinos Juniors", "Juventus", "River Plate", "Cruzeiro", "Lazio", "Barcelona", "PSG", "Villarreal"]
            },
            {
                "titulo": "Artilheiro da Copa de 2010",
                "resposta_oculta": "diego forlan",
                "clubes": ["Independiente", "Manchester United", "Villarreal", "Atlético de Madrid", "Inter de Milão", "Internacional", "Cerezo Osaka", "Peñarol"]
            },
            {
                "titulo": "Mil Gols (Segundo Ele Mesmo)",
                "resposta_oculta": "tulio maravilha",
                "clubes": ["Goiás", "Botafogo", "Corinthians", "Vitória", "Fluminense", "Cruzeiro", "São Caetano", "Vila Nova"]
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

        self.stdout.write(self.style.SUCCESS("\nConcluído! Todos os bancos estão atualizados."))
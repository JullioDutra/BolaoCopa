from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio, Clube, JogadorBanco

class Command(BaseCommand):
    help = 'Povoa o banco de dados centralizado de Clubes, Jogadores e Desafios'

    def handle(self, *args, **kwargs):
# ==========================================
        # 1. DADOS DOS ELENCOS (Campinho)
        # ==========================================
        elencos = [
            {
                "titulo": "Palmeiras 1999 (Libertadores)",
                "jogadores": [
                    {"nome": "Marcos", "posicao": "Goleiro"},
                    {"nome": "Arce", "posicao": "Lateral Direito"},
                    {"nome": "Júnior Baiano", "posicao": "Zagueiro"},
                    {"nome": "Roque Júnior", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"},
                    {"nome": "César Sampaio", "posicao": "Volante"},
                    {"nome": "Rogério", "posicao": "Volante"},
                    {"nome": "Zinho", "posicao": "Meia"},
                    {"nome": "Alex", "posicao": "Meia-Atacante"},
                    {"nome": "Paulo Nunes", "posicao": "Atacante"},
                    {"nome": "Oséas", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Vasco 2000 (Mercosul/Brasileirão)",
                "jogadores": [
                    {"nome": "Hélton", "posicao": "Goleiro"},
                    {"nome": "Clébson", "posicao": "Lateral Direito"},
                    {"nome": "Odvan", "posicao": "Zagueiro"},
                    {"nome": "Júnior Baiano", "posicao": "Zagueiro"},
                    {"nome": "Jorginho Paulista", "posicao": "Lateral Esquerdo"},
                    {"nome": "Jorginho", "posicao": "Volante"},
                    {"nome": "Juninho Pernambucano", "posicao": "Meia"},
                    {"nome": "Juninho Paulista", "posicao": "Meia-Atacante"},
                    {"nome": "Euller", "posicao": "Atacante"},
                    {"nome": "Romário", "posicao": "Centroavante"},
                    {"nome": "Edmundo", "posicao": "Atacante"},
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
                    {"nome": "Aristizábal", "posicao": "Atacante"},
                    {"nome": "Deivid", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "São Paulo 1992 (Mundial)",
                "jogadores": [
                    {"nome": "Zetti", "posicao": "Goleiro"},
                    {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Antônio Carlos", "posicao": "Zagueiro"},
                    {"nome": "Ronaldão", "posicao": "Zagueiro"},
                    {"nome": "Ronaldo Luís", "posicao": "Lateral Esquerdo"},
                    {"nome": "Pintado", "posicao": "Volante"},
                    {"nome": "Toninho Cerezo", "posicao": "Volante"},
                    {"nome": "Raí", "posicao": "Meia-Atacante"},
                    {"nome": "Müller", "posicao": "Atacante"},
                    {"nome": "Palhinha", "posicao": "Segundo Atacante"},
                    {"nome": "Macedo", "posicao": "Atacante"},
                ]
            },
            {
                "titulo": "Santos 2011 (Libertadores)",
                "jogadores": [
                    {"nome": "Rafael Cabral", "posicao": "Goleiro"},
                    {"nome": "Danilo", "posicao": "Lateral Direito"},
                    {"nome": "Edu Dracena", "posicao": "Zagueiro"},
                    {"nome": "Durval", "posicao": "Zagueiro"},
                    {"nome": "Léo", "posicao": "Lateral Esquerdo"},
                    {"nome": "Arouca", "posicao": "Volante"},
                    {"nome": "Adriano", "posicao": "Volante"},
                    {"nome": "Elano", "posicao": "Meia"},
                    {"nome": "Ganso", "posicao": "Meia-Atacante"},
                    {"nome": "Neymar", "posicao": "Ponta Esquerda"},
                    {"nome": "Borges", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Milan 2005 (A Lenda Europeia)",
                "jogadores": [
                    {"nome": "Dida", "posicao": "Goleiro"},
                    {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Stam", "posicao": "Zagueiro"},
                    {"nome": "Nesta", "posicao": "Zagueiro"},
                    {"nome": "Maldini", "posicao": "Lateral Esquerdo"},
                    {"nome": "Pirlo", "posicao": "Volante"},
                    {"nome": "Gattuso", "posicao": "Meia Central"},
                    {"nome": "Seedorf", "posicao": "Meia Esquerda"},
                    {"nome": "Kaká", "posicao": "Meia-Atacante"},
                    {"nome": "Shevchenko", "posicao": "Atacante"},
                    {"nome": "Crespo", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Internazionale 2010 (Tríplice Coroa)",
                "jogadores": [
                    {"nome": "Júlio César", "posicao": "Goleiro"},
                    {"nome": "Maicon", "posicao": "Lateral Direito"},
                    {"nome": "Lúcio", "posicao": "Zagueiro"},
                    {"nome": "Samuel", "posicao": "Zagueiro"},
                    {"nome": "Zanetti", "posicao": "Lateral Esquerdo"},
                    {"nome": "Cambiasso", "posicao": "Volante"},
                    {"nome": "Thiago Motta", "posicao": "Meia Central"},
                    {"nome": "Sneijder", "posicao": "Meia-Atacante"},
                    {"nome": "Eto'o", "posicao": "Ponta Direita"},
                    {"nome": "Pandev", "posicao": "Ponta Esquerda"},
                    {"nome": "Milito", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Itália 2006 (Copa do Mundo)",
                "jogadores": [
                    {"nome": "Buffon", "posicao": "Goleiro"},
                    {"nome": "Zambrotta", "posicao": "Lateral Direito"},
                    {"nome": "Cannavaro", "posicao": "Zagueiro"},
                    {"nome": "Materazzi", "posicao": "Zagueiro"},
                    {"nome": "Grosso", "posicao": "Lateral Esquerdo"},
                    {"nome": "Gattuso", "posicao": "Volante"},
                    {"nome": "Pirlo", "posicao": "Volante"},
                    {"nome": "Camoranesi", "posicao": "Meia Direita"},
                    {"nome": "Perrotta", "posicao": "Meia Esquerda"},
                    {"nome": "Totti", "posicao": "Meia-Atacante"},
                    {"nome": "Luca Toni", "posicao": "Centroavante"},
                ]
            }
        ]

        # ==========================================
        # 2. DADOS DAS TRAJETÓRIAS (Escudos)
        # ==========================================
        trajetorias = [
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
            {
                "titulo": "Maestro de Istambul",
                "resposta_oculta": "alex",
                "clubes": ["Coritiba", "Palmeiras", "Flamengo", "Cruzeiro", "Parma", "Fenerbahçe"]
            },
            {
                "titulo": "Zagueiro Monstro",
                "resposta_oculta": "thiago silva",
                "clubes": ["RS Futebol", "Juventude", "Porto", "Dynamo Moscow", "Fluminense", "Milan", "PSG", "Chelsea"]
            },
            {
                "titulo": "Rei do Pistoleiro",
                "resposta_oculta": "luis suarez",
                "clubes": ["Nacional", "Groningen", "Ajax", "Liverpool", "Barcelona", "Atlético de Madrid", "Grêmio", "Inter Miami"]
            },
            {
                "titulo": "O Gigante Sueco",
                "resposta_oculta": "ibrahimovic",
                "clubes": ["Malmö", "Ajax", "Juventus", "Inter de Milão", "Barcelona", "Milan", "PSG", "Manchester United", "LA Galaxy"]
            },
            {
                "titulo": "Muralha de Gelo",
                "resposta_oculta": "dida",
                "clubes": ["Vitória", "Cruzeiro", "Lugano", "Corinthians", "Milan", "Portuguesa", "Grêmio", "Internacional"]
            },
            {
                "titulo": "Velho Vamp",
                "resposta_oculta": "vampeta",
                "clubes": ["Vitória", "PSV", "VVV-Venlo", "Fluminense", "Corinthians", "Inter de Milão", "PSG", "Flamengo", "Brasiliense"]
            },
            {
                "titulo": "Capita do Penta",
                "resposta_oculta": "cafu",
                "clubes": ["São Paulo", "Real Zaragoza", "Juventude", "Palmeiras", "Roma", "Milan"]
            },
            {
                "titulo": "O Fideo",
                "resposta_oculta": "di maria",
                "clubes": ["Rosario Central", "Benfica", "Real Madrid", "Manchester United", "PSG", "Juventus"]
            },
            {
                "titulo": "Rei do Egito",
                "resposta_oculta": "salah",
                "clubes": ["Al Mokawloon", "Basel", "Chelsea", "Fiorentina", "Roma", "Liverpool"]
            },
            {
                "titulo": "Pequeno Mágico",
                "resposta_oculta": "philippe coutinho",
                "clubes": ["Vasco", "Inter de Milão", "Espanyol", "Liverpool", "Barcelona", "Bayern de Munique", "Aston Villa", "Al-Duhail"]
            },
            {
                "titulo": "O Rei Arturo",
                "resposta_oculta": "vidal",
                "clubes": ["Colo-Colo", "Bayer Leverkusen", "Juventus", "Bayern de Munique", "Barcelona", "Inter de Milão", "Flamengo", "Athletico Paranaense"]
            },
            {
                "titulo": "O Bruxo",
                "resposta_oculta": "ronaldinho",
                "clubes": ["Grêmio", "PSG", "Barcelona", "Milan", "Flamengo", "Atlético Mineiro", "Querétaro", "Fluminense"]
            },
            {
                "titulo": "Fenômeno",
                "resposta_oculta": "ronaldo",
                "clubes": ["Cruzeiro", "PSV", "Barcelona", "Inter de Milão", "Real Madrid", "Milan", "Corinthians"]
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
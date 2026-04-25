from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio

class Command(BaseCommand):
    help = 'Adiciona um catálogo extenso e caprichado de Duelos 1x1'

    def handle(self, *args, **kwargs):
        # ==========================================
        # 1. DADOS DOS ELENCOS (Campinho)
        # ==========================================
        elencos = [
            {
                "titulo": "Atlético Mineiro 2013 (Libertadores)",
                "jogadores": [
                    {"nome": "Victor", "posicao": "Goleiro"},
                    {"nome": "Marcos Rocha", "posicao": "Lateral Direito"},
                    {"nome": "Leonardo Silva", "posicao": "Zagueiro"},
                    {"nome": "Réver", "posicao": "Zagueiro"},
                    {"nome": "Richarlyson", "posicao": "Lateral Esquerdo"},
                    {"nome": "Pierre", "posicao": "Volante"},
                    {"nome": "Josué", "posicao": "Volante"},
                    {"nome": "Ronaldinho", "posicao": "Meia-Atacante"},
                    {"nome": "Bernard", "posicao": "Meia-Atacante"},
                    {"nome": "Diego Tardelli", "posicao": "Atacante"},
                    {"nome": "Jô", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Goiás 2005 (Surpresa do Brasileirão)",
                "jogadores": [
                    {"nome": "Harlei", "posicao": "Goleiro"},
                    {"nome": "Paulo Baier", "posicao": "Lateral Direito"},
                    {"nome": "Aldo", "posicao": "Zagueiro"},
                    {"nome": "Julio Santos", "posicao": "Zagueiro"},
                    {"nome": "Jadílson", "posicao": "Lateral Esquerdo"},
                    {"nome": "Cléber Gaúcho", "posicao": "Volante"},
                    {"nome": "Romerito", "posicao": "Meia"},
                    {"nome": "Rodrigo Tabata", "posicao": "Meia-Atacante"},
                    {"nome": "Souza", "posicao": "Atacante"},
                    {"nome": "Dimba", "posicao": "Centroavante"},
                    {"nome": "Jorge Amorim", "posicao": "Zagueiro"},
                ]
            },
            {
                "titulo": "Arsenal 2003/04 (Os Invencíveis)",
                "jogadores": [
                    {"nome": "Lehmann", "posicao": "Goleiro"},
                    {"nome": "Lauren", "posicao": "Lateral Direito"},
                    {"nome": "Sol Campbell", "posicao": "Zagueiro"},
                    {"nome": "Kolo Touré", "posicao": "Zagueiro"},
                    {"nome": "Ashley Cole", "posicao": "Lateral Esquerdo"},
                    {"nome": "Gilberto Silva", "posicao": "Volante"},
                    {"nome": "Patrick Vieira", "posicao": "Meia Central"},
                    {"nome": "Ljungberg", "posicao": "Meia Direita"},
                    {"nome": "Robert Pires", "posicao": "Meia Esquerda"},
                    {"nome": "Dennis Bergkamp", "posicao": "Segundo Atacante"},
                    {"nome": "Thierry Henry", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "São Paulo 2005 (Mundial)",
                "jogadores": [
                    {"nome": "Rogério Ceni", "posicao": "Goleiro"},
                    {"nome": "Cicinho", "posicao": "Ala Direito"},
                    {"nome": "Fabão", "posicao": "Zagueiro"},
                    {"nome": "Lugano", "posicao": "Zagueiro"},
                    {"nome": "Edcarlos", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Ala Esquerdo"},
                    {"nome": "Mineiro", "posicao": "Volante"},
                    {"nome": "Josué", "posicao": "Volante"},
                    {"nome": "Danilo", "posicao": "Meia-Atacante"},
                    {"nome": "Amoroso", "posicao": "Atacante"},
                    {"nome": "Aloísio", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Flamengo 1981 (Mundial)",
                "jogadores": [
                    {"nome": "Raul", "posicao": "Goleiro"},
                    {"nome": "Leandro", "posicao": "Lateral Direito"},
                    {"nome": "Marinho", "posicao": "Zagueiro"},
                    {"nome": "Mozer", "posicao": "Zagueiro"},
                    {"nome": "Júnior", "posicao": "Lateral Esquerdo"},
                    {"nome": "Andrade", "posicao": "Volante"},
                    {"nome": "Adílio", "posicao": "Meia"},
                    {"nome": "Zico", "posicao": "Meia-Atacante"},
                    {"nome": "Tita", "posicao": "Ponta Direita"},
                    {"nome": "Lico", "posicao": "Ponta Esquerda"},
                    {"nome": "Nunes", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Brasil 1970 (Copa do Mundo)",
                "jogadores": [
                    {"nome": "Félix", "posicao": "Goleiro"},
                    {"nome": "Carlos Alberto", "posicao": "Lateral Direito"},
                    {"nome": "Brito", "posicao": "Zagueiro"},
                    {"nome": "Piazza", "posicao": "Zagueiro"},
                    {"nome": "Everaldo", "posicao": "Lateral Esquerdo"},
                    {"nome": "Clodoaldo", "posicao": "Volante"},
                    {"nome": "Gérson", "posicao": "Meia"},
                    {"nome": "Rivellino", "posicao": "Meia-Atacante"},
                    {"nome": "Jairzinho", "posicao": "Ponta Direita"},
                    {"nome": "Pelé", "posicao": "Segundo Atacante"},
                    {"nome": "Tostão", "posicao": "Centroavante"},
                ]
            },
            {
                "titulo": "Corinthians 2012 (Mundial)",
                "jogadores": [
                    {"nome": "Cássio", "posicao": "Goleiro"},
                    {"nome": "Alessandro", "posicao": "Lateral Direito"},
                    {"nome": "Chicão", "posicao": "Zagueiro"},
                    {"nome": "Paulo André", "posicao": "Zagueiro"},
                    {"nome": "Fábio Santos", "posicao": "Lateral Esquerdo"},
                    {"nome": "Ralf", "posicao": "Volante"},
                    {"nome": "Paulinho", "posicao": "Volante"},
                    {"nome": "Danilo", "posicao": "Meia"},
                    {"nome": "Jorge Henrique", "posicao": "Atacante"},
                    {"nome": "Emerson Sheik", "posicao": "Atacante"},
                    {"nome": "Guerrero", "posicao": "Centroavante"},
                ]
            }
        ]

        # ==========================================
        # 2. DADOS DAS TRAJETÓRIAS (Escudos)
        # ==========================================
        trajetorias = [
            {
                "titulo": "Zagueiro Artilheiro (Premier League)",
                "resposta_oculta": "gabriel magalhaes",
                "clubes": ["Avaí", "Lille", "Troyes", "Dinamo Zagreb", "Arsenal"]
            },
            {
                "titulo": "O Maestro Holandês",
                "resposta_oculta": "seedorf",
                "clubes": ["Ajax", "Sampdoria", "Real Madrid", "Inter de Milão", "Milan", "Botafogo"]
            },
            {
                "titulo": "Xerife Francês",
                "resposta_oculta": "william saliba",
                "clubes": ["Saint-Étienne", "Arsenal", "Nice", "Marseille", "Arsenal"]
            },
            {
                "titulo": "El Apache",
                "resposta_oculta": "tevez",
                "clubes": ["Boca Juniors", "Corinthians", "West Ham", "Manchester United", "Manchester City", "Juventus", "Boca Juniors"]
            },
            {
                "titulo": "Lenda dos Cárpatos",
                "resposta_oculta": "hagi",
                "clubes": ["Farul Constanta", "Sportul Studentesc", "Steaua Bucareste", "Real Madrid", "Brescia", "Barcelona", "Galatasaray"]
            },
            {
                "titulo": "O Pitbull",
                "resposta_oculta": "felipe melo",
                "clubes": ["Flamengo", "Cruzeiro", "Grêmio", "Mallorca", "Fiorentina", "Juventus", "Galatasaray", "Inter de Milão", "Palmeiras", "Fluminense"]
            },
            {
                "titulo": "Nômade Anelka",
                "resposta_oculta": "anelka",
                "clubes": ["PSG", "Arsenal", "Real Madrid", "Liverpool", "Manchester City", "Fenerbahçe", "Bolton", "Chelsea", "Juventus"]
            },
            {
                "titulo": "O Gringo Mais Amado",
                "resposta_oculta": "petkovic",
                "clubes": ["Estrela Vermelha", "Real Madrid", "Vitória", "Flamengo", "Vasco", "Fluminense", "Goiás", "Santos", "Atlético Mineiro"]
            },
            {
                "titulo": "O Animal",
                "resposta_oculta": "edmundo",
                "clubes": ["Vasco", "Palmeiras", "Flamengo", "Corinthians", "Fiorentina", "Santos", "Napoli", "Cruzeiro", "Tokyo Verdy", "Figueirense"]
            },
            {
                "titulo": "Mago Luso-Brasileiro",
                "resposta_oculta": "deco",
                "clubes": ["Corinthians", "Alverca", "Salgueiros", "Porto", "Barcelona", "Chelsea", "Fluminense"]
            }
        ]

        self.stdout.write(self.style.WARNING("========================================"))
        self.stdout.write(self.style.WARNING(" INICIANDO POVOAMENTO DE DUELOS 1x1"))
        self.stdout.write(self.style.WARNING("========================================\n"))

        # --- PROCESSANDO ELENCOS ---
        self.stdout.write(self.style.MIGRATE_HEADING("Adicionando Elencos Clássicos..."))
        for dados_elenco in elencos:
            categoria, criada = CategoriaDesafio.objects.get_or_create(
                titulo=dados_elenco["titulo"],
                tipo='elenco'
            )
            
            if criada:
                for j in dados_elenco["jogadores"]:
                    ItemDesafio.objects.create(
                        categoria=categoria,
                        nome=j["nome"],
                        posicao_tatica=j["posicao"],
                        ordem=0
                    )
                self.stdout.write(self.style.SUCCESS(f' [+] Elenco "{categoria.titulo}" adicionado!'))
            else:
                self.stdout.write(self.style.NOTICE(f' [~] Elenco "{categoria.titulo}" já existia. Pulando...'))

        self.stdout.write("\n")

        # --- PROCESSANDO TRAJETÓRIAS ---
        self.stdout.write(self.style.MIGRATE_HEADING("Adicionando Trajetórias Misteriosas..."))
        for dados_traj in trajetorias:
            categoria, criada = CategoriaDesafio.objects.get_or_create(
                titulo=dados_traj["titulo"],
                tipo='trajetoria',
                resposta_oculta=dados_traj["resposta_oculta"]
            )
            
            if criada:
                for indice, clube in enumerate(dados_traj["clubes"]):
                    ItemDesafio.objects.create(
                        categoria=categoria,
                        nome=clube,
                        ordem=indice + 1
                    )
                self.stdout.write(self.style.SUCCESS(f' [+] Trajetória "{categoria.titulo}" adicionada!'))
            else:
                self.stdout.write(self.style.NOTICE(f' [~] Trajetória "{categoria.titulo}" já existia. Pulando...'))

        self.stdout.write(self.style.WARNING("\n========================================"))
        self.stdout.write(self.style.SUCCESS(" POVOAMENTO CONCLUÍDO COM SUCESSO!"))
        self.stdout.write(self.style.WARNING("========================================"))
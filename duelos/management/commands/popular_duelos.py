from django.core.management.base import BaseCommand
from duelos.models import CategoriaDesafio, ItemDesafio

class Command(BaseCommand):
    help = 'Adiciona vários desafios de Elenco e Trajetória de uma só vez'

    def handle(self, *args, **kwargs):
        # 1. DADOS DOS ELENCOS (Campinho)
        elencos = [
            {
                "titulo": "Brasil 2002",
                "jogadores": [
                    {"nome": "Marcos", "posicao": "Goleiro"},
                    {"nome": "Cafu", "posicao": "Lateral Direito"},
                    {"nome": "Lucio", "posicao": "Zagueiro"},
                    {"nome": "Roque Junior", "posicao": "Zagueiro"},
                    {"nome": "Edmilson", "posicao": "Zagueiro"},
                    {"nome": "Roberto Carlos", "posicao": "Lateral Esquerdo"},
                    {"nome": "Gilberto Silva", "posicao": "Volante"},
                    {"nome": "Kleberson", "posicao": "Meia"},
                    {"nome": "Ronaldinho", "posicao": "Meia-Atacante"},
                    {"nome": "Rivaldo", "posicao": "Meia-Atacante"},
                    {"nome": "Ronaldo", "posicao": "Atacante"},
                ]
            },
            # Pode adicionar "Espanha 2010", "Flamengo 2019", etc. aqui...
        ]

        # 2. DADOS DAS TRAJETÓRIAS (Escudos)
        trajetorias = [
            {
                "titulo": "Menino da Vila",
                "resposta_oculta": "neymar",
                "clubes": ["Santos", "Barcelona", "PSG", "Al-Hilal"]
            },
            {
                "titulo": "O Robô",
                "resposta_oculta": "cristiano ronaldo",
                "clubes": ["Sporting", "Manchester United", "Real Madrid", "Juventus", "Al-Nassr"]
            },
            {
                "titulo": "Imperador",
                "resposta_oculta": "adriano",
                "clubes": ["Flamengo", "Inter de Milao", "Fiorentina", "Parma", "Sao Paulo", "Roma", "Corinthians"]
            }
        ]

        self.stdout.write("Iniciando a inserção de dados...")

        # --- PROCESSANDO ELENCOS ---
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
                self.stdout.write(self.style.SUCCESS(f'Sucesso: Elenco "{categoria.titulo}" adicionado!'))
            else:
                self.stdout.write(self.style.WARNING(f'Aviso: Elenco "{categoria.titulo}" já existia. Pulando...'))


        # --- PROCESSANDO TRAJETÓRIAS ---
        for dados_traj in trajetorias:
            categoria, criada = CategoriaDesafio.objects.get_or_create(
                titulo=dados_traj["titulo"],
                tipo='trajetoria',
                resposta_oculta=dados_traj["resposta_oculta"]
            )
            
            if criada:
                # O enumerate começa do 0, então somamos 1 para a ordem (1º clube, 2º clube...)
                for indice, clube in enumerate(dados_traj["clubes"]):
                    ItemDesafio.objects.create(
                        categoria=categoria,
                        nome=clube,
                        ordem=indice + 1
                    )
                self.stdout.write(self.style.SUCCESS(f'Sucesso: Trajetória "{categoria.titulo}" adicionada!'))
            else:
                self.stdout.write(self.style.WARNING(f'Aviso: Trajetória "{categoria.titulo}" já existia. Pulando...'))

        self.stdout.write(self.style.SUCCESS('Finalizado! Todos os dados foram processados.'))
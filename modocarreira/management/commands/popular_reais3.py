from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from modocarreira.models import ServidorConfig, Campeonato, Clube, Avatar
import random

class Command(BaseCommand):
    help = 'Popula a base de dados com os 20 Clubes e Jogadores REAIS e ATUAIS da Série C 2026.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('A transferir os craques da Terceirona para o Metaverso...'))

        config = ServidorConfig.objects.first()
        if not config:
            self.stdout.write(self.style.ERROR('Por favor, corra primeiro o "popular_carreira" para criar o servidor.'))
            return

        # ==========================================
        # BASE DE DADOS REAL — Brasileirão Série C 2026 (20 clubes)
        # NOTA: a Série C tem cobertura de imprensa bem menor que A/B, então o
        # número de jogadores confirmados por clube varia (times mais
        # midiáticos como Paysandu, Guarani, Amazonas e Botafogo-PB têm mais
        # nomes verificados do que clubes menores como Anápolis ou Itabaiana).
        # ==========================================
        dados_reais = {
            'Paysandu': {
                'sigla': 'PAY', 'prestigio': 48, 'orcamento': 120000, 'divisao': 'C',
                'jogadores': [
                    ('Ítalo', 'ST', 63), ('Juninho', 'ST', 60), ('Kleiton Pego', 'ST', 59),
                    ('Marcinho', 'AM', 60), ('Caio Mello', 'DM', 58),
                ]
            },
            'Guarani': {
                'sigla': 'GUA', 'prestigio': 50, 'orcamento': 130000, 'divisao': 'C',
                'jogadores': [
                    ('Caíque França', 'GK', 59), ('Ynaiã', 'CB', 58), ('Emerson', 'LB', 57),
                    ('Ralf', 'DM', 60), ('Isaque', 'AM', 59), ('Hebert', 'ST', 61),
                ]
            },
            'Botafogo-PB': {
                'sigla': 'BPB', 'prestigio': 49, 'orcamento': 120000, 'divisao': 'C',
                'jogadores': [
                    ('Igor Morais', 'CB', 58), ('Yan Souto', 'CB', 57), ('Edson Alves', 'CB', 57),
                    ('Nenê', 'AM', 62),
                ]
            },
            'Amazonas': {
                'sigla': 'AMA', 'prestigio': 49, 'orcamento': 120000, 'divisao': 'C',
                'jogadores': [
                    ('Renan', 'GK', 58), ('Iury', 'RB', 57), ('Yuri', 'CB', 58),
                    ('Rafael Vitor', 'CB', 57), ('Fabiano', 'LB', 58), ('Rafael Tavares', 'AM', 59),
                    ('Nico Schiappacasse', 'ST', 59),
                ]
            },
            'Santa Cruz': {
                'sigla': 'SCR', 'prestigio': 48, 'orcamento': 115000, 'divisao': 'C',
                'jogadores': [
                    ('Gabriel', 'GK', 57), ('Saulo', 'GK', 56), ('Everaldo', 'ST', 60),
                ]
            },
            'Volta Redonda': {
                'sigla': 'VOL', 'prestigio': 47, 'orcamento': 110000, 'divisao': 'C',
                'jogadores': [
                    ('Felipe Avelino', 'GK', 58), ('Lucas Rocha', 'CB', 57), ('Oswaldo Blanco', 'ST', 59),
                    ('Ygor Catatau', 'ST', 58),
                ]
            },
            'Ferroviária': {
                'sigla': 'FER', 'prestigio': 46, 'orcamento': 105000, 'divisao': 'C',
                'jogadores': [
                    ('Felipe Rodrigues', 'RB', 56), ('Gustavo Medina', 'CB', 57), ('Allison', 'ST', 58),
                    ('Denilson Silva', 'ST', 57),
                ]
            },
            'Inter de Limeira': {
                'sigla': 'ILI', 'prestigio': 46, 'orcamento': 105000, 'divisao': 'C',
                'jogadores': [
                    ('Yan Silva', 'CB', 56), ('Lucas Buchecha', 'AM', 57), ('Claudinho', 'AM', 58),
                    ('Miguel Bianconi', 'ST', 58),
                ]
            },
            'Ituano': {
                'sigla': 'ITU', 'prestigio': 47, 'orcamento': 110000, 'divisao': 'C',
                'jogadores': [
                    ('Tiago Silva', 'CB', 57), ('Dal Pian', 'LB', 57), ('Nelsinho', 'DM', 58),
                    ('Fernando Canesin', 'ST', 58), ('Gabriel Razera', 'ST', 57),
                ]
            },
            'Brusque': {
                'sigla': 'BRU', 'prestigio': 46, 'orcamento': 105000, 'divisao': 'C',
                'jogadores': [
                    ('Matheus Nogueira', 'GK', 57), ('Raimar', 'LB', 56), ('Gazão', 'AM', 58),
                    ('Adrianinho', 'ST', 58),
                ]
            },
            'Caxias': {
                'sigla': 'CAX', 'prestigio': 44, 'orcamento': 95000, 'divisao': 'C',
                'jogadores': [
                    ('Salatiel', 'ST', 57),
                ]
            },
            'Confiança': {
                'sigla': 'CON', 'prestigio': 45, 'orcamento': 100000, 'divisao': 'C',
                'jogadores': [
                    ('Ícaro', 'CB', 56), ('PK', 'AM', 56), ('João Pedro', 'ST', 57),
                    ('Maikon Aquino', 'ST', 57),
                ]
            },
            'Itabaiana': {
                'sigla': 'ITA', 'prestigio': 42, 'orcamento': 85000, 'divisao': 'C',
                'jogadores': [
                    ('Karl', 'AM', 55), ('Cleiton', 'ST', 57),
                ]
            },
            'Figueirense': {
                'sigla': 'FIG', 'prestigio': 43, 'orcamento': 90000, 'divisao': 'C',
                'jogadores': [
                    ('Breno', 'AM', 55), ('Hyuri', 'ST', 57),
                ]
            },
            'Ypiranga': {
                'sigla': 'YPI', 'prestigio': 42, 'orcamento': 85000, 'divisao': 'C',
                'jogadores': [
                    ('Cleiton', 'RB', 54), ('Nicolas Schulz', 'LB', 56),
                ]
            },
            'Maringá': {
                'sigla': 'MAR', 'prestigio': 41, 'orcamento': 80000, 'divisao': 'C',
                'jogadores': [
                    ('Felipe', 'CB', 54), ('Caíque Cálito', 'ST', 56),
                ]
            },
            'Floresta': {
                'sigla': 'FLO', 'prestigio': 42, 'orcamento': 85000, 'divisao': 'C',
                'jogadores': [
                    ('Eliandro', 'RB', 54), ('Daniel Triano', 'ST', 55), ('Jhony', 'ST', 55),
                    ('Garraty', 'ST', 56),
                ]
            },
            'Barra-SC': {
                'sigla': 'BAR', 'prestigio': 40, 'orcamento': 75000, 'divisao': 'C',
                'jogadores': [
                    ('Éverton Alemão', 'CB', 54), ('Tetê', 'DM', 55),
                ]
            },
            'Anápolis': {
                'sigla': 'ANA', 'prestigio': 39, 'orcamento': 70000, 'divisao': 'C',
                'jogadores': [
                    ('Cássio Gabriel', 'AM', 54),
                ]
            },
            'Maranhão': {
                'sigla': 'MAC', 'prestigio': 41, 'orcamento': 80000, 'divisao': 'C',
                'jogadores': [
                    ('Jean', 'GK', 55), ('Maurício', 'RB', 53), ('Lucão', 'CB', 54),
                    ('Tibúrcio', 'CB', 54), ('André Radija', 'LB', 53), ('Railson', 'DM', 54),
                    ('Vander', 'CM', 54), ('Vagalume', 'CM', 55), ('Will', 'RW', 55),
                    ('Rafael', 'AM', 54), ('Felipe Cruz', 'ST', 56),
                ]
            },
        }

        with transaction.atomic():
            Campeonato.objects.get_or_create(nome='Brasileirão Série C', temporada=config.temporada_atual, tipo='liga', divisao='C')

            user_bot, _ = User.objects.get_or_create(username='cbf_oficial', defaults={'email': 'cbf@cartolandia.com'})
            if not user_bot.password:
                user_bot.set_password('senha_segura_123')
                user_bot.save()

            jogadores_criados = 0
            clubes_criados = 0

            for nome_clube, info in dados_reais.items():
                clube, criado = Clube.objects.get_or_create(
                    nome=nome_clube,
                    defaults={
                        'sigla': info['sigla'],
                        'divisao': info['divisao'],
                        'orcamento': info['orcamento'],
                        'prestigio_reputacao': info['prestigio']
                    }
                )
                if criado:
                    clubes_criados += 1

                for nome_jogador, posicao, ovr in info['jogadores']:
                    if posicao in ['GK', 'CB', 'DM', 'LB', 'RB']:
                        arq = 'xerife'
                    elif posicao in ['CM', 'AM']:
                        arq = 'maestro'
                    elif posicao in ['ST']:
                        arq = 'matador'
                    elif posicao in ['RW', 'LW']:
                        arq = 'motorzinho'
                    else:
                        arq = 'motorzinho'

                    if not Avatar.objects.filter(nome_camisa=nome_jogador, clube_atual=clube).exists():
                        username_jogador = f"{nome_jogador.replace(' ', '').lower()}_{info['sigla'].lower()}"
                        user_jogador, _ = User.objects.get_or_create(username=username_jogador)

                        Avatar.objects.create(
                            usuario=user_jogador,
                            nome_camisa=nome_jogador,
                            arquetipo=arq,
                            posicao_preferida=posicao,
                            clube_atual=clube,
                            temporada_nascimento=config.temporada_atual,
                            idade_inicial=random.randint(18, 33),
                            teto_potencial_oculto=ovr + random.randint(3, 10),
                            fisico=ovr - 2,
                            tecnica=ovr,
                            inteligencia=ovr + 2,
                            media_fama=ovr,
                            salario_rodada=int(ovr * 80),
                            pontos_acao_diarios=1
                        )
                        jogadores_criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n SUCESSO! {clubes_criados} clubes e {jogadores_criados} craques da Série C foram transferidos para o Metaverso!'
        ))
        self.stdout.write('São os aventureiros da Terceirona, sonhando com o acesso à Segundona!')

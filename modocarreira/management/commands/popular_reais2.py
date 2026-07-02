from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from modocarreira.models import ServidorConfig, Campeonato, Clube, Avatar
import random

class Command(BaseCommand):
    help = 'Popula a base de dados com os 20 Clubes e Jogadores REAIS e ATUAIS da Série B 2026.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('A transferir os craques da Segundona para o Metaverso...'))

        config = ServidorConfig.objects.first()
        if not config:
            self.stdout.write(self.style.ERROR('Por favor, corra primeiro o "popular_carreira" para criar o servidor.'))
            return

        # ==========================================
        # BASE DE DADOS REAL — Brasileirão Série B 2026 (20 clubes)
        # Escalações-base (Time-Base) reais de cada equipe na temporada.
        # ==========================================
        dados_reais = {
            'Fortaleza': {
                'sigla': 'FOR', 'prestigio': 66, 'orcamento': 350000, 'divisao': 'B',
                'jogadores': [
                    ('Brenno', 'GK', 74), ('Britez', 'CB', 71), ('Lucas Gazal', 'CB', 70),
                    ('Luan Freitas', 'LB', 70), ('Mailton', 'RB', 71), ('Pierre', 'DM', 72),
                    ('Lucas Sasha', 'CM', 71), ('Lucas Crispim', 'AM', 73), ('Fuentes', 'CM', 70),
                    ('Pochettino', 'ST', 73), ('Luiz Fernando', 'ST', 71),
                ]
            },
            'Ceará': {
                'sigla': 'CEA', 'prestigio': 65, 'orcamento': 320000, 'divisao': 'B',
                'jogadores': [
                    ('Richard', 'GK', 72), ('Alex Silva', 'RB', 69), ('Éder', 'CB', 70),
                    ('Luizão', 'CB', 69), ('Fernando', 'LB', 69), ('Lucas Lima', 'CM', 71),
                    ('Vinícius Zanocelo', 'DM', 71), ('Vina', 'AM', 72), ('Matheus Araújo', 'CM', 70),
                    ('Matheusinho', 'RW', 70), ('Wendel Silva', 'ST', 70),
                ]
            },
            'Sport': {
                'sigla': 'SPT', 'prestigio': 62, 'orcamento': 250000, 'divisao': 'B',
                'jogadores': [
                    ('Thiago Couto', 'GK', 71), ('Augusto Pucci', 'RB', 68), ('Marcelo Ajul', 'CB', 69),
                    ('Marcelo Benevenuto', 'CB', 69), ('Felipinho', 'LB', 68), ('Zé Gabriel', 'DM', 69),
                    ('Zé Lucas', 'CM', 68), ('Yago Felipe', 'AM', 71), ('Gustavo Maia', 'RW', 69),
                    ('Barletta', 'ST', 69), ('Iury Castilho', 'ST', 70),
                ]
            },
            'Juventude': {
                'sigla': 'JUV', 'prestigio': 60, 'orcamento': 230000, 'divisao': 'B',
                'jogadores': [
                    ('Jandrey', 'GK', 69), ('Rodrigo Sam', 'RB', 66), ('Messias', 'CB', 67),
                    ('Marcos Paulo', 'CB', 66), ('Ray Ramos', 'DM', 67), ('Lucas Mineiro', 'CM', 68),
                    ('Pablo Roberto', 'CM', 66), ('Mandaca', 'AM', 68), ('Gabriel Taliari', 'RW', 68),
                    ('Alan Kardec', 'ST', 70),
                ]
            },
            'Goiás': {
                'sigla': 'GOI', 'prestigio': 63, 'orcamento': 280000, 'divisao': 'B',
                'jogadores': [
                    ('Tadeu', 'GK', 70), ('Diego Caito', 'RB', 67), ('Lucas Ribeiro', 'CB', 68),
                    ('Luisão', 'CB', 67), ('Nicolas', 'LB', 67), ('Lucas Rodrigues', 'CM', 68),
                    ('Lourenço', 'CM', 68), ('Gege', 'CM', 66), ('Lucas Lima', 'AM', 70),
                    ('Jean Carlos', 'ST', 69), ('Anselmo Ramon', 'ST', 71),
                ]
            },
            'Novorizontino': {
                'sigla': 'NOV', 'prestigio': 59, 'orcamento': 210000, 'divisao': 'B',
                'jogadores': [
                    ('César', 'GK', 68), ('Castrillón', 'RB', 66), ('Dantas', 'CB', 66),
                    ('Eduardo Brock', 'CB', 67), ('Patrick', 'LB', 66), ('Léo Naldi', 'CM', 67),
                    ('Luís Oyama', 'DM', 68), ('Tavinho', 'AM', 68), ('Rômulo', 'CM', 66),
                    ('Vinícius Paiva', 'ST', 67), ('Robson', 'ST', 68),
                ]
            },
            'América-MG': {
                'sigla': 'AME', 'prestigio': 61, 'orcamento': 240000, 'divisao': 'B',
                'jogadores': [
                    ('Gustavo', 'GK', 67), ('Nathan', 'RB', 65), ('Rafa Barcelos', 'CB', 66),
                    ('Emerson', 'CB', 65), ('Maguinho', 'LB', 65), ('Felipe Amaral', 'CM', 66),
                    ('Val Soares', 'DM', 66), ('Eduardo Person', 'CM', 65), ('Artur', 'AM', 67),
                    ('Willian Bigode', 'ST', 66), ('Paulo Victor', 'ST', 65),
                ]
            },
            'Atlético-GO': {
                'sigla': 'ACG', 'prestigio': 60, 'orcamento': 260000, 'divisao': 'B',
                'jogadores': [
                    ('Paulo Vitor', 'GK', 67), ('Matheus Ribeiro', 'RB', 65), ('Tito', 'CB', 66),
                    ('Adriano Martins', 'CB', 65), ('Guilherme Lopes', 'LB', 65), ('Leandro Vilela', 'CM', 66),
                    ('Cristiano', 'DM', 66), ('Igor Henrique', 'CM', 65), ('Guilherme Marques', 'AM', 66),
                    ('Marrony', 'RW', 68), ('Léo Jacó', 'ST', 66),
                ]
            },
            'Avaí': {
                'sigla': 'AVA', 'prestigio': 58, 'orcamento': 180000, 'divisao': 'B',
                'jogadores': [
                    ('Léo Aragão', 'GK', 65), ('Gasolina', 'RB', 63), ('Alysson', 'CB', 64),
                    ('Baldini', 'CB', 63), ('DG', 'LB', 63), ('Zé', 'DM', 64),
                    ('Luiz Henrique', 'CM', 64), ('Penha', 'CM', 63), ('Jean', 'AM', 64),
                    ('Thayllon', 'ST', 65), ('Avenatti', 'ST', 66),
                ]
            },
            'CRB': {
                'sigla': 'CRB', 'prestigio': 61, 'orcamento': 260000, 'divisao': 'B',
                'jogadores': [
                    ('Matheus Albino', 'GK', 66), ('Hereda', 'RB', 64), ('Bressan', 'CB', 65),
                    ('Fábio Alemão', 'CB', 64), ('Lucas Lovat', 'LB', 64), ('Pedro Castro', 'DM', 65),
                    ('Crystopher', 'CM', 64), ('Danielzinho', 'AM', 65), ('Douglas Baggio', 'RW', 66),
                    ('Dadá Belmonte', 'AM', 65), ('Mikael', 'ST', 66),
                ]
            },
            'Criciúma': {
                'sigla': 'CRI', 'prestigio': 60, 'orcamento': 250000, 'divisao': 'B',
                'jogadores': [
                    ('Alisson', 'GK', 66), ('Marcinho', 'RB', 64), ('Rodrigo', 'CB', 65),
                    ('Luciano Castán', 'CB', 65), ('Marcelo Hermes', 'LB', 64), ('Jean Irmer', 'CM', 65),
                    ('Eduardo', 'DM', 64), ('Sandry', 'CM', 65), ('Jhonata Robert', 'AM', 65),
                    ('Diego Gonçalves', 'RW', 66), ('Waguininho', 'ST', 66),
                ]
            },
            'Cuiabá': {
                'sigla': 'CUI', 'prestigio': 59, 'orcamento': 240000, 'divisao': 'B',
                'jogadores': [
                    ('Marcelo Carné', 'GK', 65), ('Vitor Mendes', 'CB', 64), ('Luís Soares', 'CB', 64),
                    ('Calebe', 'LB', 63), ('Nino Paraíba', 'RB', 65), ('Raul', 'DM', 64),
                    ('Pepê', 'CM', 65), ('Marlon', 'CM', 63), ('Rodrigo Rodrigues', 'RW', 64),
                    ('Kauan Cristtyan', 'ST', 64), ('Vinícius Peixoto', 'ST', 65),
                ]
            },
            'Náutico': {
                'sigla': 'NAU', 'prestigio': 56, 'orcamento': 190000, 'divisao': 'B',
                'jogadores': [
                    ('Muriel', 'GK', 64), ('Arnaldo', 'RB', 62), ('Mateus Silva', 'CB', 62),
                    ('Igor Fernandes', 'CB', 62), ('Yuri Silva', 'LB', 62), ('Samuel', 'DM', 63),
                    ('Wenderson', 'CM', 62), ('Dodô', 'AM', 63), ('Junior Todinho', 'ST', 64),
                    ('Vinícius', 'ST', 62), ('Paulo Sérgio', 'ST', 62),
                ]
            },
            'Operário-PR': {
                'sigla': 'OPE', 'prestigio': 55, 'orcamento': 170000, 'divisao': 'B',
                'jogadores': [
                    ('Vágner', 'GK', 63), ('Mikael Doka', 'RB', 61), ('Cuenú', 'CB', 62),
                    ('Miranda', 'CB', 61), ('Moraes', 'LB', 61), ('Índio', 'DM', 62),
                    ('Vinícius Diniz', 'CM', 61), ('Boschilia', 'AM', 64), ('Hildeberto Pereira', 'RW', 62),
                    ('Aylon', 'ST', 62), ('Pereira', 'ST', 61),
                ]
            },
            'Ponte Preta': {
                'sigla': 'PON', 'prestigio': 57, 'orcamento': 180000, 'divisao': 'B',
                'jogadores': [
                    ('Diogo Silva', 'GK', 63), ('Pacheco', 'RB', 61), ('David Braz', 'CB', 65),
                    ('Lucas Cunha', 'CB', 61), ('Kevyson', 'LB', 61), ('Rodrigo Souza', 'CM', 62),
                    ('Rodrigo Saravia', 'DM', 62), ('Léo Gomes', 'CM', 61), ('Élvis', 'AM', 63),
                    ('William Pottker', 'ST', 65), ('David da Hora', 'ST', 62),
                ]
            },
            'Vila Nova': {
                'sigla': 'VNO', 'prestigio': 56, 'orcamento': 175000, 'divisao': 'B',
                'jogadores': [
                    ('Dalberson', 'GK', 62), ('Elias', 'RB', 60), ('Pedro Romano', 'CB', 61),
                    ('Tiago Pagnussat', 'CB', 61), ('Willian Formiga', 'LB', 60), ('Nathan Camargo', 'CM', 61),
                    ('João Vieira', 'CM', 61), ('Marquinhos Gabriel', 'AM', 62), ('André Luís', 'RW', 61),
                    ('Dellatorre', 'ST', 63), ('Ryan', 'ST', 61),
                ]
            },
            'Athletic': {
                'sigla': 'ATH', 'prestigio': 50, 'orcamento': 140000, 'divisao': 'B',
                'jogadores': [
                    ('Jhonatan Luiz', 'GK', 59), ('Diogo Batista', 'RB', 57), ('Jhonatan Silva', 'CB', 58),
                    ('Belezi', 'CB', 57), ('Zeca', 'LB', 57), ('Gian Cabezas', 'CM', 58),
                    ('Ian Luccas', 'DM', 57), ('David Braga', 'AM', 58), ('Ruan Assis', 'RW', 58),
                    ('Dixon Vera', 'ST', 58), ('Ronaldo Tavares', 'ST', 57),
                ]
            },
            'Botafogo-SP': {
                'sigla': 'BSP', 'prestigio': 51, 'orcamento': 150000, 'divisao': 'B',
                'jogadores': [
                    ('Victor Souza', 'GK', 60), ('Gabriel Inocêncio', 'RB', 57), ('Ericson', 'CB', 58),
                    ('Villar', 'CB', 58), ('Patrick Brey', 'LB', 57), ('Leandro Maciel', 'CM', 58),
                    ('Morelli', 'DM', 57), ('Rafael Gava', 'AM', 58), ('Jefferson Nem', 'RW', 58),
                    ('Kelvin', 'ST', 59), ('Hygor', 'ST', 57),
                ]
            },
            'Londrina': {
                'sigla': 'LON', 'prestigio': 52, 'orcamento': 150000, 'divisao': 'B',
                'jogadores': [
                    ('Maurício Kozlinski', 'GK', 59), ('Maurício Mucuri', 'RB', 57), ('Wallace Reis', 'CB', 58),
                    ('Yago Lincoln', 'CB', 57), ('Rafael Monteiro', 'LB', 57), ('André Luiz', 'CM', 58),
                    ('Lucas Marques', 'DM', 57), ('Vitinho Mota', 'AM', 58), ('Vitor Jacaré', 'RW', 58),
                    ('Iago Teles', 'ST', 58), ('Gilberto', 'ST', 58),
                ]
            },
            'São Bernardo': {
                'sigla': 'SBE', 'prestigio': 48, 'orcamento': 130000, 'divisao': 'B',
                'jogadores': [
                    ('Alex Alves', 'GK', 58), ('Rodrigo Ferreira', 'RB', 56), ('Pablo', 'CB', 57),
                    ('Augusto', 'CB', 56), ('Pará', 'LB', 56), ('Marcão Silva', 'CM', 57),
                    ('Júnior Urso', 'DM', 58), ('João Paulo', 'AM', 57), ('Pedro Vitor', 'RW', 57),
                    ('Felipe Garcia', 'ST', 57), ('Fabrício Daniel', 'ST', 57),
                ]
            },
        }

        with transaction.atomic():
            Campeonato.objects.get_or_create(nome='Brasileirão Série B', temporada=config.temporada_atual, tipo='liga', divisao='B')

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
                            idade_inicial=random.randint(19, 34),
                            teto_potencial_oculto=ovr + random.randint(2, 8),
                            fisico=ovr - 2,
                            tecnica=ovr,
                            inteligencia=ovr + 2,
                            media_fama=ovr,
                            salario_rodada=int(ovr * 150),
                            pontos_acao_diarios=1
                        )
                        jogadores_criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n SUCESSO! {clubes_criados} clubes e {jogadores_criados} craques da Série B foram transferidos para o Metaverso!'
        ))
        self.stdout.write('Fique de olho: muitos destes jogadores brigam pelo acesso à elite!')

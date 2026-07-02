from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from modocarreira.models import ServidorConfig, Campeonato, Clube, Avatar
import random

class Command(BaseCommand):
    help = 'Popula a base de dados com os 20 Clubes e Jogadores REAIS e ATUAIS do Brasileirão Série A 2026.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('A transferir os craques reais para o Metaverso...'))

        config = ServidorConfig.objects.first()
        if not config:
            self.stdout.write(self.style.ERROR('Por favor, corra primeiro o "popular_carreira" para criar o servidor.'))
            return

        # ==========================================
        # BASE DE DADOS REAL — Brasileirão Série A 2026 (20 clubes)
        # Escalações-base (Time-Base) reais de cada equipe na temporada.
        # ==========================================
        dados_reais = {
            'Flamengo': {
                'sigla': 'FLA', 'prestigio': 92, 'orcamento': 1500000, 'divisao': 'A',
                'jogadores': [
                    ('Rossi', 'GK', 84), ('Varela', 'RB', 82), ('Léo Ortiz', 'CB', 84),
                    ('Léo Pereira', 'CB', 83), ('Alex Sandro', 'LB', 82), ('Erick Pulgar', 'DM', 83),
                    ('Jorginho', 'CM', 85), ('De Arrascaeta', 'AM', 89), ('Carrascal', 'RW', 83),
                    ('Bruno Henrique', 'LW', 81), ('Pedro', 'ST', 88),
                ]
            },
            'Palmeiras': {
                'sigla': 'PAL', 'prestigio': 92, 'orcamento': 1450000, 'divisao': 'A',
                'jogadores': [
                    ('Carlos Miguel', 'GK', 82), ('Khellven', 'RB', 81), ('Gustavo Gómez', 'CB', 86),
                    ('Murilo', 'CB', 83), ('Piquerez', 'LB', 84), ('Marlon Freitas', 'DM', 82),
                    ('Andreas Pereira', 'CM', 84), ('Felipe Anderson', 'RW', 83), ('Allan', 'AM', 79),
                    ('Flaco López', 'ST', 82), ('Vitor Roque', 'ST', 85),
                ]
            },
            'São Paulo': {
                'sigla': 'SAO', 'prestigio': 85, 'orcamento': 950000, 'divisao': 'A',
                'jogadores': [
                    ('Rafael', 'GK', 82), ('Ferraresi', 'CB', 82), ('Arboleda', 'CB', 82),
                    ('Alan Franco', 'CB', 79), ('Maik', 'RB', 77), ('Pablo Maia', 'DM', 81),
                    ('Bobadilla', 'CM', 79), ('Marcos Antônio', 'CM', 78), ('Enzo Díaz', 'LB', 77),
                    ('Lucas Moura', 'AM', 84), ('Calleri', 'ST', 84),
                ]
            },
            'Corinthians': {
                'sigla': 'COR', 'prestigio': 84, 'orcamento': 850000, 'divisao': 'A',
                'jogadores': [
                    ('Hugo Souza', 'GK', 80), ('Matheuzinho', 'RB', 78), ('André Ramalho', 'CB', 79),
                    ('Gustavo Henrique', 'CB', 78), ('Matheus Bidu', 'LB', 76), ('Carrillo', 'RW', 79),
                    ('Raniele', 'DM', 80), ('Breno Bidon', 'CM', 78), ('Rodrigo Garro', 'AM', 84),
                    ('Memphis Depay', 'LW', 86), ('Yuri Alberto', 'ST', 81),
                ]
            },
            'Atlético-MG': {
                'sigla': 'CAM', 'prestigio': 86, 'orcamento': 1000000, 'divisao': 'A',
                'jogadores': [
                    ('Everson', 'GK', 82), ('Preciado', 'RB', 78), ('Ruan', 'CB', 79),
                    ('Vitor Hugo', 'CB', 78), ('Renan Lodi', 'LB', 81), ('Alan Franco', 'DM', 78),
                    ('Maycon', 'CM', 79), ('Cuello', 'RW', 80), ('Bernard', 'AM', 82),
                    ('Dudu', 'LW', 82), ('Hulk', 'ST', 87),
                ]
            },
            'Botafogo': {
                'sigla': 'BOT', 'prestigio': 86, 'orcamento': 1250000, 'divisao': 'A',
                'jogadores': [
                    ('Neto', 'GK', 79), ('Barboza', 'CB', 81), ('Newton', 'CB', 77),
                    ('Bastos', 'CB', 80), ('Vitinho', 'RB', 82), ('Allan', 'DM', 80),
                    ('Danilo', 'CM', 79), ('Alex Telles', 'LB', 81), ('Artur', 'RW', 79),
                    ('Montoro', 'AM', 80), ('Arthur Cabral', 'ST', 83),
                ]
            },
            'Bahia': {
                'sigla': 'BAH', 'prestigio': 80, 'orcamento': 700000, 'divisao': 'A',
                'jogadores': [
                    ('Ronaldo', 'GK', 78), ('Román Gómez', 'CB', 77), ('Gabriel Xavier', 'CB', 76),
                    ('Kanu', 'CB', 78), ('Luciano Juba', 'LB', 80), ('Acevedo', 'DM', 78),
                    ('Erick', 'CM', 79), ('Michel Araújo', 'AM', 79), ('Ademir', 'LW', 78),
                    ('Iago', 'ST', 78), ('Willian José', 'ST', 79),
                ]
            },
            'Fluminense': {
                'sigla': 'FLU', 'prestigio': 82, 'orcamento': 800000, 'divisao': 'A',
                'jogadores': [
                    ('Fábio', 'GK', 81), ('Samuel Xavier', 'RB', 77), ('Freytes', 'CB', 78),
                    ('Jammes', 'CB', 77), ('Guilherme Arana', 'LB', 82), ('Martinelli', 'DM', 81),
                    ('Hércules', 'CM', 79), ('Savarino', 'AM', 83), ('Serna', 'RW', 78),
                    ('Canobbio', 'LW', 78), ('Everaldo', 'ST', 78),
                ]
            },
            'Cruzeiro': {
                'sigla': 'CRU', 'prestigio': 84, 'orcamento': 900000, 'divisao': 'A',
                'jogadores': [
                    ('Cássio', 'GK', 81), ('William', 'RB', 78), ('Fabrício Bruno', 'CB', 83),
                    ('Jonathan Jesus', 'CB', 77), ('Kaiki', 'LB', 76), ('Lucas Silva', 'DM', 80),
                    ('Lucas Romero', 'CM', 79), ('Gerson', 'CM', 84), ('Matheus Pereira', 'AM', 83),
                    ('Arroyo', 'LW', 79), ('Kaio Jorge', 'ST', 84),
                ]
            },
            'Grêmio': {
                'sigla': 'GRE', 'prestigio': 81, 'orcamento': 750000, 'divisao': 'A',
                'jogadores': [
                    ('Weverton', 'GK', 82), ('Marcos Rocha', 'RB', 77), ('Gustavo Martins', 'CB', 77),
                    ('Wagner Leonardo', 'CB', 77), ('Caio Paulista', 'LB', 79), ('Arthur', 'DM', 80),
                    ('Edenilson', 'CM', 78), ('Cristaldo', 'AM', 82), ('Tetê', 'RW', 80),
                    ('Carlos Vinícius', 'ST', 79), ('Enamorado', 'LW', 77),
                ]
            },
            'Internacional': {
                'sigla': 'INT', 'prestigio': 80, 'orcamento': 780000, 'divisao': 'A',
                'jogadores': [
                    ('Rochet', 'GK', 80), ('Bruno Gomes', 'RB', 76), ('Mercado', 'CB', 78),
                    ('Félix Torres', 'CB', 79), ('Bernabei', 'LB', 78), ('Thiago Maia', 'DM', 79),
                    ('Rodrigo Villagra', 'CM', 77), ('Alan Patrick', 'AM', 82), ('Carbonero', 'RW', 78),
                    ('Vitinho', 'LW', 78), ('Borré', 'ST', 81),
                ]
            },
            'Vasco da Gama': {
                'sigla': 'VAS', 'prestigio': 78, 'orcamento': 650000, 'divisao': 'A',
                'jogadores': [
                    ('Léo Jardim', 'GK', 80), ('Paulo Henrique', 'RB', 75), ('Cuesta', 'CB', 76),
                    ('Robert Renan', 'CB', 77), ('Lucas Piton', 'LB', 79), ('Thiago Mendes', 'DM', 78),
                    ('Barros', 'CM', 76), ('Andrés Gómez', 'CM', 77), ('Philippe Coutinho', 'AM', 83),
                    ('GB', 'RW', 75), ('Nuno Moreira', 'LW', 76),
                ]
            },
            'Santos': {
                'sigla': 'SAN', 'prestigio': 80, 'orcamento': 700000, 'divisao': 'A',
                'jogadores': [
                    ('Gabriel Brazão', 'GK', 76), ('Igor Vinícius', 'RB', 76), ('Adonis Frías', 'CB', 76),
                    ('Zé Ivaldo', 'CB', 75), ('Souza', 'LB', 75), ('Willian Arão', 'DM', 78),
                    ('João Schmidt', 'CM', 76), ('Neymar', 'AM', 88), ('Rollheiser', 'RW', 78),
                    ('Gabigol', 'ST', 80), ('Barreal', 'LW', 77),
                ]
            },
            'Red Bull Bragantino': {
                'sigla': 'RBB', 'prestigio': 76, 'orcamento': 600000, 'divisao': 'A',
                'jogadores': [
                    ('Cleiton', 'GK', 76), ('Agustin Sant\u2019Anna', 'RB', 75), ('Gustavo Marques', 'CB', 76),
                    ('Alix Vinícius', 'CB', 75), ('Juninho Capixaba', 'LB', 78), ('Gabriel', 'DM', 76),
                    ('Eric Ramires', 'CM', 76), ('Jhon Jhon', 'AM', 77), ('Lucas Barbosa', 'RW', 78),
                    ('Henry Mosquera', 'LW', 76), ('Eduardo Sasha', 'ST', 79),
                ]
            },
            'Vitória': {
                'sigla': 'VIT', 'prestigio': 70, 'orcamento': 400000, 'divisao': 'A',
                'jogadores': [
                    ('Gabriel Vasconcellos', 'GK', 73), ('Matheuzinho', 'RB', 72), ('Camutanga', 'CB', 75),
                    ('Riccieli', 'CB', 74), ('Mateus Silva', 'LB', 72), ('Gabriel Baralhas', 'DM', 74),
                    ('Ronald', 'CM', 73), ('Ramon', 'CM', 72), ('Erick', 'RW', 73),
                    ('Aitor Cantalapiedra', 'AM', 75), ('Renato Kayzer', 'ST', 76),
                ]
            },
            'Mirassol': {
                'sigla': 'MIR', 'prestigio': 68, 'orcamento': 380000, 'divisao': 'A',
                'jogadores': [
                    ('Walter', 'GK', 74), ('Daniel Borges', 'RB', 72), ('João Victor', 'CB', 74),
                    ('Luiz Otávio', 'CB', 73), ('Reinaldo', 'LB', 77), ('Neto Moura', 'DM', 73),
                    ('Yuri Lara', 'CM', 74), ('Shaylon', 'AM', 75), ('Lucas Mugni', 'CM', 74),
                    ('Alesson', 'RW', 73), ('André Luís', 'ST', 74),
                ]
            },
            'Coritiba': {
                'sigla': 'CFC', 'prestigio': 65, 'orcamento': 350000, 'divisao': 'A',
                'jogadores': [
                    ('Pedro Morisco', 'GK', 71), ('Tinga', 'RB', 70), ('Maicon', 'CB', 73),
                    ('Jacy', 'CB', 71), ('Bruno Melo', 'LB', 72), ('Willian Oliveira', 'DM', 72),
                    ('Sebastián Gómez', 'CM', 73), ('Josué', 'CM', 71), ('Lucas Ronier', 'RW', 75),
                    ('Pedro Rocha', 'AM', 74), ('Breno Lopes', 'ST', 74),
                ]
            },
            'Athletico-PR': {
                'sigla': 'CAP', 'prestigio': 72, 'orcamento': 500000, 'divisao': 'A',
                'jogadores': [
                    ('Santos', 'GK', 74), ('Benavídez', 'CB', 73), ('Carlos Terán', 'CB', 73),
                    ('Arthur Dias', 'CB', 72), ('Lucas Esquivel', 'LB', 73), ('Jadson', 'CM', 74),
                    ('Portilla', 'CM', 73), ('Felipinho', 'RW', 73), ('Bruno Zapelli', 'AM', 76),
                    ('Kevin Viveros', 'ST', 77), ('Julimar', 'ST', 73),
                ]
            },
            'Chapecoense': {
                'sigla': 'CHA', 'prestigio': 60, 'orcamento': 280000, 'divisao': 'A',
                'jogadores': [
                    ('Rafael Santos', 'GK', 70), ('Victor Caetano', 'RB', 69), ('Eduardo Doma', 'CB', 70),
                    ('João Paulo', 'CB', 69), ('Marcos Vinícius', 'CB', 69), ('Walter Clar', 'LB', 69),
                    ('Camilo', 'CM', 71), ('Rafael Carvalheira', 'CM', 69), ('Giovanni Augusto', 'AM', 74),
                    ('Marcinho', 'RW', 70), ('Italo', 'ST', 71),
                ]
            },
            'Remo': {
                'sigla': 'REM', 'prestigio': 62, 'orcamento': 300000, 'divisao': 'A',
                'jogadores': [
                    ('Marcelo Rangel', 'GK', 71), ('João Lucas', 'RB', 69), ('Klaus', 'CB', 71),
                    ('Léo Andrade', 'CB', 70), ('Sávio', 'LB', 69), ('Zé Ricardo', 'DM', 70),
                    ('Patrick de Paula', 'CM', 74), ('Patrick', 'AM', 70), ('Yago Pikachu', 'RW', 75),
                    ('João Pedro', 'ST', 71), ('Nicolás Ferreira', 'LW', 70),
                ]
            },
        }

        with transaction.atomic():
            # Cria a Série A
            Campeonato.objects.get_or_create(nome='Brasileirão Série A', temporada=config.temporada_atual, tipo='liga', divisao='A')

            # Utilizador "fantasma" para os jogadores reais serem controlados pelo servidor
            user_bot, _ = User.objects.get_or_create(username='cbf_oficial', defaults={'email': 'cbf@cartolandia.com'})
            if not user_bot.password:
                user_bot.set_password('senha_segura_123')
                user_bot.save()

            jogadores_criados = 0
            clubes_criados = 0

            for nome_clube, info in dados_reais.items():
                # 1. Cria o Clube
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

                # 2. Cria os Jogadores Reais do Clube
                for nome_jogador, posicao, ovr in info['jogadores']:
                    # Mapear a posição para o arquétipo correto do seu jogo
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

                    # Impede que crie duplicados se correr o script duas vezes
                    if not Avatar.objects.filter(nome_camisa=nome_jogador, clube_atual=clube).exists():
                        # Cria utilizadores únicos falsos para cada um (exigência do seu model Avatar)
                        username_jogador = f"{nome_jogador.replace(' ', '').replace('\u2019', '').lower()}_{info['sigla'].lower()}"
                        user_jogador, _ = User.objects.get_or_create(username=username_jogador)

                        Avatar.objects.create(
                            usuario=user_jogador,
                            nome_camisa=nome_jogador,
                            arquetipo=arq,
                            posicao_preferida=posicao,
                            clube_atual=clube,
                            temporada_nascimento=config.temporada_atual,
                            idade_inicial=random.randint(20, 34),  # Idade simulada
                            teto_potencial_oculto=ovr + random.randint(1, 5),  # Potencial um pouco maior que o OVR atual
                            fisico=ovr - 2,
                            tecnica=ovr,
                            inteligencia=ovr + 2,
                            media_fama=ovr,
                            salario_rodada=int(ovr * 300),
                            pontos_acao_diarios=1
                        )
                        jogadores_criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n SUCESSO! {clubes_criados} clubes e {jogadores_criados} craques reais foram transferidos para o Metaverso!'
        ))
        self.stdout.write('Vá à aba "Mercado" e veja quem tem dinheiro para tirar o Neymar do Santos ou o Coutinho do Vasco!')

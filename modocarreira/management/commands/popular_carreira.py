import random
from django.core.management.base import BaseCommand
from modocarreira.models import ServidorConfig, Campeonato, Clube
from modocarreira.services import gerar_calendario_liga

class Command(BaseCommand):
    help = 'O Big Bang: Popula o banco de dados com a configuração inicial, clubes e calendário da Série C.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Iniciando a criação do Metaverso da Cartolândia...'))

        # 1. CRIAR O RELÓGIO DO SERVIDOR
        config, created = ServidorConfig.objects.get_or_create(
            id=1,
            defaults={
                'temporada_atual': 1,
                'rodada_atual': 1,
                'fase_mercado_aberto': True,
                'periodo_data_fifa': False
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('ServidorConfig (Temporada 1) inicializado!'))
        else:
            self.stdout.write('ServidorConfig já existe. Ignorando.')

        # 2. CRIAR OS CLUBES FUNDADORES (Série C)
        clubes_serie_c = [
            {'nome': 'Íbis Sport Club', 'sigla': 'IBI', 'orcamento': 100000, 'prestigio': 10},
            {'nome': 'XV de Piracicaba', 'sigla': 'XVP', 'orcamento': 150000, 'prestigio': 30},
            {'nome': 'Bangu Atlético Clube', 'sigla': 'BAN', 'orcamento': 200000, 'prestigio': 40},
            {'nome': 'Juventus da Mooca', 'sigla': 'JUV', 'orcamento': 180000, 'prestigio': 35},
            {'nome': 'Madureira', 'sigla': 'MAD', 'orcamento': 160000, 'prestigio': 25},
            {'nome': 'Ferroviário', 'sigla': 'FER', 'orcamento': 250000, 'prestigio': 45},
            {'nome': 'Olaria', 'sigla': 'OLA', 'orcamento': 120000, 'prestigio': 20},
            {'nome': 'Nacional-AM', 'sigla': 'NAC', 'orcamento': 220000, 'prestigio': 38},
        ]

        for c_data in clubes_serie_c:
            clube, c_created = Clube.objects.get_or_create(
                nome=c_data['nome'],
                defaults={
                    'sigla': c_data['sigla'],
                    'divisao': 'C',
                    'orcamento': c_data['orcamento'],
                    'prestigio_reputacao': c_data['prestigio']
                }
            )
            if c_created:
                self.stdout.write(f'Clube fundado: {clube.nome} ({clube.sigla})')

        # 3. CRIAR O CAMPEONATO
        camp_serie_c, camp_created = Campeonato.objects.get_or_create(
            nome='Brasileirão Série C',
            temporada=config.temporada_atual,
            tipo='liga',
            divisao='C'
        )
        
        if camp_created:
            self.stdout.write(self.style.SUCCESS(f'\nCampeonato criado: {camp_serie_c.nome}'))
            
            # 4. GERAR O CALENDÁRIO
            self.stdout.write('A gerar o calendário de partidas (Turno e Returno)...')
            gerar_calendario_liga(camp_serie_c)
            self.stdout.write(self.style.SUCCESS('Calendário de confrontos gerado com sucesso!'))
        else:
            self.stdout.write('\nO Campeonato já existe. O calendário não foi recriado para evitar jogos duplicados.')

        self.stdout.write(self.style.SUCCESS('\nO BIG BANG FOI UM SUCESSO! O Metaverso está pronto para receber os primeiros jogadores reais.'))

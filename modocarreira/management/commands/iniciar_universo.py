from django.core.management.base import BaseCommand
from modocarreira.models import ServidorConfig, Campeonato
from modocarreira.services import gerar_calendario_liga

class Command(BaseCommand):
    help = 'Inicia a Temporada 1 e gera todos os calendários do Modo Carreira'

    def handle(self, *args, **kwargs):
        # 1. Configurar o Relógio do Servidor
        config, created = ServidorConfig.objects.get_or_create(id=1, defaults={'temporada_atual': 1, 'rodada_atual': 1})
        
        self.stdout.write(f"Iniciando Temporada {config.temporada_atual}...")

        # 2. Criar os Campeonatos (A, B e C)
        divisoes = ['A', 'B', 'C']
        for div in divisoes:
            camp, _ = Campeonato.objects.get_or_create(
                temporada=config.temporada_atual,
                divisao=div,
                defaults={'nome': f'Brasileirão Série {div}', 'tipo': 'pontos_corridos'}
            )
            
            # 3. Gerar os Jogos
            self.stdout.write(f"Gerando calendário da Série {div}...")
            gerar_calendario_liga(camp)
            
        self.stdout.write(self.style.SUCCESS("BIG BANG CONCLUÍDO! O Metaverso começou e os calendários foram gerados!"))

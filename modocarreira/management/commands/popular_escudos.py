from django.core.management.base import BaseCommand
from modocarreira.models import Clube
# Assumindo que a sua app 'duelos' tem o modelo ClubeFutebol com os escudos reais
from duelos.models import ClubeFutebol 

class Command(BaseCommand):
    help = 'Sincroniza os escudos reais da app Duelos para o Modo Carreira'

    def handle(self, *args, **kwargs):
        clubes_carreira = Clube.objects.all()
        atualizados = 0
        falhas = 0

        self.stdout.write("A iniciar a sincronização de escudos...")

        for clube in clubes_carreira:
            # Procura um clube na app Duelos que tenha o mesmo nome (ignorando maiúsculas/minúsculas)
            clube_real = ClubeFutebol.objects.filter(nome__icontains=clube.nome).first()
            
            # Se encontrou o clube e ele tem uma imagem de escudo guardada
            if clube_real and clube_real.escudo:
                clube.escudo = clube_real.escudo
                clube.save()
                self.stdout.write(self.style.SUCCESS(f'[OK] Escudo importado: {clube.nome}'))
                atualizados += 1
            else:
                self.stdout.write(self.style.WARNING(f'[FALHA] Sem escudo para: {clube.nome}'))
                falhas += 1

        self.stdout.write(self.style.SUCCESS(f'\nRESUMO: {atualizados} escudos importados. {falhas} não encontrados.'))

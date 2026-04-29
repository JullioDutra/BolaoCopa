import os
from django.core.management.base import BaseCommand
from django.conf import settings
from duelos.models import Clube
import unicodedata

class Command(BaseCommand):
    help = 'Sincroniza os clubes da base de dados com os ficheiros existentes no banco de escudos'

    def normalizar_nome(self, nome):
        nome_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
        return nome_sem_acentos.lower().replace(' ', '_')

    def handle(self, *args, **kwargs):
        # Caminho para a pasta onde guarda os escudos
        caminho_escudos = os.path.join(settings.MEDIA_ROOT, 'duelos', 'clubes')
        
        clubes = Clube.objects.all()
        sucessos = 0

        for clube in clubes:
            # Se o clube já tem o caminho no banco, mas queremos garantir que está certo
            nome_arquivo = f"{self.normalizar_nome(clube.nome)}.png"
            caminho_relativo = os.path.join('duelos', 'clubes', nome_arquivo)
            caminho_absoluto = os.path.join(settings.MEDIA_ROOT, caminho_relativo)

            if os.path.exists(caminho_absoluto):
                clube.escudo = caminho_relativo
                clube.save()
                self.stdout.write(self.style.SUCCESS(f'[V] Vinculado: {clube.nome} -> {nome_arquivo}'))
                sucessos += 1
            else:
                self.stdout.write(self.style.WARNING(f'[!] Arquivo não encontrado para: {clube.nome} ({nome_arquivo})'))

        self.stdout.write(self.style.SUCCESS(f'\nSincronização concluída! {sucessos} clubes vinculados ao banco de escudos.'))
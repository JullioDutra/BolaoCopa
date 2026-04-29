import requests
import unicodedata
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube

class Command(BaseCommand):
    help = 'Baixa os escudos de TODOS os clubes em formato estrito .PNG'

    def normalizar_nome(self, nome):
        """Remove acentos, espaços e deixa tudo em minúsculas para a URL do site."""
        nome_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
        return nome_sem_acentos.lower().replace(' ', '-')

    def handle(self, *args, **kwargs):
        # Dicionário atualizado APENAS com links PNG diretos da Wikipedia (renderizados)
        urls_internacionais = {
            "Real Madrid": "https://logodetimes.com/times/real-madrid/logo-real-madrid-256.png",
            "Barcelona": "https://logodetimes.com/times/barcelona/logo-barcelona-256.png",
            "Milan": "https://logodetimes.com/times/milan/logo-milan-256.png",
            "Inter de Milão": "https://logodetimes.com/times/inter-de-milao/logo-inter-de-milao-256.png",
            "Juventus": "https://logodetimes.com/times/juventus/logo-juventus-256.png",
            "Chelsea": "https://logodetimes.com/times/chelsea/logo-chelsea-256.png",
            "Manchester United": "https://logodetimes.com/times/manchester-united/logo-manchester-united-256.png",
            "Bayern de Munique": "https://logodetimes.com/times/bayern-de-munique/logo-bayern-de-munique-256.png",
            "PSG": "https://logodetimes.com/times/psg/logo-psg-256.png",
            "Arsenal": "https://logodetimes.com/times/arsenal/logo-arsenal-256.png",
            "Liverpool": "https://logodetimes.com/times/liverpool/logo-liverpool-256.png",
            "Manchester City": "https://logodetimes.com/times/manchester-city/logo-manchester-city-256.png",
            "Tottenham": "https://logodetimes.com/times/tottenham/logo-tottenham-256.png",
            "Borussia Dortmund": "https://logodetimes.com/times/borussia-dortmund/logo-borussia-dortmund-256.png",
            "Bayer Leverkusen": "https://logodetimes.com/times/bayer-leverkusen/logo-bayer-leverkusen-256.png",
            "Atlético de Madrid": "https://logodetimes.com/times/atletico-de-madrid/logo-atletico-de-madrid-256.png",
            "Roma": "https://logodetimes.com/times/roma/logo-roma-256.png",
            "Napoli": "https://logodetimes.com/times/napoli/logo-napoli-256.png",
            "Lazio": "https://logodetimes.com/times/lazio/logo-lazio-256.png",
            "Fiorentina": "https://logodetimes.com/times/fiorentina/logo-fiorentina-256.png",
            "Ajax": "https://logodetimes.com/times/ajax/logo-ajax-256.png",
            "PSV": "https://logodetimes.com/times/psv/logo-psv-256.png",
            "Porto": "https://logodetimes.com/times/porto/logo-porto-256.png",
            "Benfica": "https://logodetimes.com/times/benfica/logo-benfica-256.png",
            "Sporting": "https://logodetimes.com/times/sporting/logo-sporting-256.png",

            "Boca Juniors": "https://logodetimes.com/times/boca-juniors/logo-boca-juniors-256.png",
            "River Plate": "https://logodetimes.com/times/river-plate/logo-river-plate-256.png",
            "San Lorenzo": "https://logodetimes.com/times/san-lorenzo/logo-san-lorenzo-256.png",
            "Racing": "https://logodetimes.com/times/racing/logo-racing-256.png",
            "Estudiantes": "https://logodetimes.com/times/estudiantes/logo-estudiantes-256.png",
            "Nacional": "https://logodetimes.com/times/nacional/logo-nacional-256.png",
            "Colo-Colo": "https://logodetimes.com/times/colo-colo/logo-colo-colo-256.png",
            "LDU": "https://logodetimes.com/times/ldu/logo-ldu-256.png",

            "Galatasaray": "https://logodetimes.com/times/galatasaray/logo-galatasaray-256.png",
            "Fenerbahçe": "https://logodetimes.com/times/fenerbahce/logo-fenerbahce-256.png",
            "Besiktas": "https://logodetimes.com/times/besiktas/logo-besiktas-256.png",
            "Zenit": "https://logodetimes.com/times/zenit/logo-zenit-256.png",
            "LA Galaxy": "https://logodetimes.com/times/la-galaxy/logo-la-galaxy-256.png",
            "Orlando City": "https://logodetimes.com/times/orlando-city/logo-orlando-city-256.png",
            "Kashima Antlers": "https://logodetimes.com/times/kashima-antlers/logo-kashima-antlers-256.png"
        }
        clubes = Clube.objects.all()
        total_clubes = clubes.count()
        
        self.stdout.write(self.style.WARNING(f"\nIniciando download APENAS EM .PNG para os {total_clubes} clubes..."))
        
        sucessos = 0
        falhas = 0

        for clube in clubes:
            # Ignora se o clube já tem escudo, para não repetir
            if clube.escudo:
                continue

            url = None

            # 1. Tenta a nossa lista de PNGs da Wikipedia
            if clube.nome in urls_internacionais:
                url = urls_internacionais[clube.nome]
            else:
                # 2. Assume que é Brasileiro e tenta o Logodetimes (que é 100% PNG)
                slug = self.normalizar_nome(clube.nome)
                url = f"https://logodetimes.com/times/{slug}/logo-{slug}-256.png"

            try:
                # Finge ser um navegador para não ser bloqueado
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                resposta = requests.get(url, stream=True, headers=headers)
                
                if resposta.status_code == 200:
                    # FORÇA a guardar sempre como ficheiro .png
                    nome_arquivo = f"{self.normalizar_nome(clube.nome)}.png"
                    
                    clube.escudo.save(nome_arquivo, ContentFile(resposta.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f'[+] {clube.nome} guardado como .PNG!'))
                    sucessos += 1
                else:
                    self.stdout.write(self.style.ERROR(f'[X] Falha no {clube.nome} (Erro 404).'))
                    falhas += 1
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'[X] Erro de rede ao baixar {clube.nome}: {e}'))
                falhas += 1

        self.stdout.write(self.style.WARNING(f"\nResumo: {sucessos} PNGs adicionados com sucesso | {falhas} falharam."))
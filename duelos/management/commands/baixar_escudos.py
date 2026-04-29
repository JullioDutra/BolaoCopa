import requests
import unicodedata
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube


class Command(BaseCommand):
    help = 'Download FINAL de escudos (100% PNG válidos e confiáveis)'

    def normalizar_nome(self, nome):
        nome = nome.lower()
        nome = unicodedata.normalize('NFD', nome)
        nome = ''.join(c for c in nome if unicodedata.category(c) != 'Mn')
        nome = nome.replace(' ', '-')
        nome = nome.replace('fc', '').replace('clube', '').replace('--', '-')
        return nome.strip('-')

    def handle(self, *args, **kwargs):

        urls_corrigidas = {
            "Vasco": "https://logodetimes.com/times/vasco-da-gama/logo-vasco-da-gama-256.png",
            "PSV": "https://logodetimes.com/times/psv-eindhoven/logo-psv-eindhoven-256.png",
            "Inter de Milão": "https://logodetimes.com/times/inter-de-milao/logo-inter-de-milao-256.png",
            "Fenerbahçe": "https://logodetimes.com/times/fenerbahce/logo-fenerbahce-256.png",
            "Espanyol": "https://logodetimes.com/times/espanyol/logo-espanyol-256.png",
            "Bayern de Munique": "https://logodetimes.com/times/bayern-de-munique/logo-bayern-de-munique-256.png",
            "Aston Villa": "https://logodetimes.com/times/aston-villa/logo-aston-villa-256.png",
            "Deportivo La Coruña": "https://logodetimes.com/times/deportivo-la-coruna/logo-deportivo-la-coruna-256.png",
            "Nacional": "https://logodetimes.com/times/nacional/logo-nacional-256.png",
            "Cruz Azul": "https://logodetimes.com/times/cruz-azul/logo-cruz-azul-256.png",
            "Monterrey": "https://logodetimes.com/times/monterrey/logo-monterrey-256.png",
            "Ajax": "https://logodetimes.com/times/ajax/logo-ajax-256.png",
            "Crystal Palace": "https://logodetimes.com/times/crystal-palace/logo-crystal-palace-256.png",
            "Independiente": "https://logodetimes.com/times/independiente/logo-independiente-256.png",
            "Atlético de Madrid": "https://logodetimes.com/times/atletico-de-madrid/logo-atletico-de-madrid-256.png",
            "Sporting": "https://logodetimes.com/times/sporting/logo-sporting-256.png",
            "Besiktas": "https://logodetimes.com/times/besiktas/logo-besiktas-256.png",
            "Goiás": "https://logodetimes.com/times/goias/logo-goias-256.png",
            "Wolfsburg": "https://logodetimes.com/times/wolfsburg/logo-wolfsburg-256.png",
            "Athletico Paranaense": "https://logodetimes.com/times/athletico-paranaense/logo-athletico-paranaense-256.png",
            "Sampdoria": "https://logodetimes.com/times/sampdoria/logo-sampdoria-256.png",
            "Fiorentina": "https://logodetimes.com/times/fiorentina/logo-fiorentina-256.png",
            "LA Galaxy": "https://logodetimes.com/times/la-galaxy/logo-la-galaxy-256.png",
            "Udinese": "https://logodetimes.com/times/udinese/logo-udinese-256.png",
            "Newell's Old Boys": "https://logodetimes.com/times/newells-old-boys/logo-newells-old-boys-256.png",
            "River Plate": "https://logodetimes.com/times/river-plate/logo-river-plate-256.png",
            "Boca Juniors": "https://logodetimes.com/times/boca-juniors/logo-boca-juniors-256.png",
            "West Ham": "https://logodetimes.com/times/west-ham/logo-west-ham-256.png",
            "Estudiantes": "https://logodetimes.com/times/estudiantes/logo-estudiantes-256.png",
            "Colo-Colo": "https://logodetimes.com/times/colo-colo/logo-colo-colo-256.png",
            "Necaxa": "https://logodetimes.com/times/necaxa/logo-necaxa-256.png",
            "Nice": "https://logodetimes.com/times/nice/logo-nice-256.png",
            "Marseille": "https://logodetimes.com/times/olympique-de-marseille/logo-olympique-de-marseille-256.png",
            "Brescia": "https://logodetimes.com/times/brescia/logo-brescia-256.png",
            "Monza": "https://logodetimes.com/times/monza/logo-monza-256.png",
            "Bayer Leverkusen": "https://logodetimes.com/times/bayer-leverkusen/logo-bayer-leverkusen-256.png",
            "Hertha Berlin": "https://logodetimes.com/times/hertha-berlin/logo-hertha-berlin-256.png",
            "Portsmouth": "https://logodetimes.com/times/portsmouth/logo-portsmouth-256.png",
            "Genoa": "https://logodetimes.com/times/genoa/logo-genoa-256.png",
            "Schalke 04": "https://logodetimes.com/times/schalke-04/logo-schalke-04-256.png",
            "Las Palmas": "https://logodetimes.com/times/las-palmas/logo-las-palmas-256.png",
            "Sassuolo": "https://logodetimes.com/times/sassuolo/logo-sassuolo-256.png",
            "Zenit": "https://logodetimes.com/times/zenit/logo-zenit-256.png",
            "Estrela Vermelha": "https://logodetimes.com/times/estrela-vermelha/logo-estrela-vermelha-256.png",
            "Racing": "https://logodetimes.com/times/racing-club/logo-racing-club-256.png",
            "Olympiacos": "https://logodetimes.com/times/olympiacos/logo-olympiacos-256.png",
            "AEK": "https://logodetimes.com/times/aek-atenas/logo-aek-atenas-256.png",
            "Benfica": "https://logodetimes.com/times/benfica/logo-benfica-256.png",
        }

        clubes = Clube.objects.all()
        faltantes = [c for c in clubes if not c.escudo]

        self.stdout.write(self.style.WARNING(f"\nResgatando {len(faltantes)} clubes..."))

        sucessos = 0
        falhas = 0

        for clube in faltantes:

            if clube.nome in urls_corrigidas:
                url = urls_corrigidas[clube.nome]
            else:
                slug = self.normalizar_nome(clube.nome)
                url = f"https://logodetimes.com/times/{slug}/logo-{slug}-256.png"

            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resposta = requests.get(url, timeout=10, headers=headers)

                if resposta.status_code == 200 and "image" in resposta.headers.get("Content-Type", ""):

                    nome_arquivo = f"{self.normalizar_nome(clube.nome)}.png"
                    clube.escudo.save(nome_arquivo, ContentFile(resposta.content), save=True)

                    self.stdout.write(self.style.SUCCESS(f'[+] {clube.nome} OK'))
                    sucessos += 1
                else:
                    self.stdout.write(self.style.ERROR(f'[X] {clube.nome} falhou'))
                    falhas += 1

            except:
                self.stdout.write(self.style.ERROR(f'[X] erro rede: {clube.nome}'))
                falhas += 1

        self.stdout.write(self.style.WARNING(f"\nFINAL: {sucessos} OK | {falhas} falhas"))import requests
import unicodedata
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube


class Command(BaseCommand):
    help = 'Download FINAL de escudos (100% PNG válidos e confiáveis)'

    def normalizar_nome(self, nome):
        nome = nome.lower()
        nome = unicodedata.normalize('NFD', nome)
        nome = ''.join(c for c in nome if unicodedata.category(c) != 'Mn')
        nome = nome.replace(' ', '-')
        nome = nome.replace('fc', '').replace('clube', '').replace('--', '-')
        return nome.strip('-')

    def handle(self, *args, **kwargs):

        urls_corrigidas = {
            "Vasco": "https://logodetimes.com/times/vasco-da-gama/logo-vasco-da-gama-256.png",
            "PSV": "https://logodetimes.com/times/psv-eindhoven/logo-psv-eindhoven-256.png",
            "Inter de Milão": "https://logodetimes.com/times/inter-de-milao/logo-inter-de-milao-256.png",
            "Fenerbahçe": "https://logodetimes.com/times/fenerbahce/logo-fenerbahce-256.png",
            "Espanyol": "https://logodetimes.com/times/espanyol/logo-espanyol-256.png",
            "Bayern de Munique": "https://logodetimes.com/times/bayern-de-munique/logo-bayern-de-munique-256.png",
            "Aston Villa": "https://logodetimes.com/times/aston-villa/logo-aston-villa-256.png",
            "Deportivo La Coruña": "https://logodetimes.com/times/deportivo-la-coruna/logo-deportivo-la-coruna-256.png",
            "Nacional": "https://logodetimes.com/times/nacional/logo-nacional-256.png",
            "Cruz Azul": "https://logodetimes.com/times/cruz-azul/logo-cruz-azul-256.png",
            "Monterrey": "https://logodetimes.com/times/monterrey/logo-monterrey-256.png",
            "Ajax": "https://logodetimes.com/times/ajax/logo-ajax-256.png",
            "Crystal Palace": "https://logodetimes.com/times/crystal-palace/logo-crystal-palace-256.png",
            "Independiente": "https://logodetimes.com/times/independiente/logo-independiente-256.png",
            "Atlético de Madrid": "https://logodetimes.com/times/atletico-de-madrid/logo-atletico-de-madrid-256.png",
            "Sporting": "https://logodetimes.com/times/sporting/logo-sporting-256.png",
            "Besiktas": "https://logodetimes.com/times/besiktas/logo-besiktas-256.png",
            "Goiás": "https://logodetimes.com/times/goias/logo-goias-256.png",
            "Wolfsburg": "https://logodetimes.com/times/wolfsburg/logo-wolfsburg-256.png",
            "Athletico Paranaense": "https://logodetimes.com/times/athletico-paranaense/logo-athletico-paranaense-256.png",
            "Sampdoria": "https://logodetimes.com/times/sampdoria/logo-sampdoria-256.png",
            "Fiorentina": "https://logodetimes.com/times/fiorentina/logo-fiorentina-256.png",
            "LA Galaxy": "https://logodetimes.com/times/la-galaxy/logo-la-galaxy-256.png",
            "Udinese": "https://logodetimes.com/times/udinese/logo-udinese-256.png",
            "Newell's Old Boys": "https://logodetimes.com/times/newells-old-boys/logo-newells-old-boys-256.png",
            "River Plate": "https://logodetimes.com/times/river-plate/logo-river-plate-256.png",
            "Boca Juniors": "https://logodetimes.com/times/boca-juniors/logo-boca-juniors-256.png",
            "West Ham": "https://logodetimes.com/times/west-ham/logo-west-ham-256.png",
            "Estudiantes": "https://logodetimes.com/times/estudiantes/logo-estudiantes-256.png",
            "Colo-Colo": "https://logodetimes.com/times/colo-colo/logo-colo-colo-256.png",
            "Necaxa": "https://logodetimes.com/times/necaxa/logo-necaxa-256.png",
            "Nice": "https://logodetimes.com/times/nice/logo-nice-256.png",
            "Marseille": "https://logodetimes.com/times/olympique-de-marseille/logo-olympique-de-marseille-256.png",
            "Brescia": "https://logodetimes.com/times/brescia/logo-brescia-256.png",
            "Monza": "https://logodetimes.com/times/monza/logo-monza-256.png",
            "Bayer Leverkusen": "https://logodetimes.com/times/bayer-leverkusen/logo-bayer-leverkusen-256.png",
            "Hertha Berlin": "https://logodetimes.com/times/hertha-berlin/logo-hertha-berlin-256.png",
            "Portsmouth": "https://logodetimes.com/times/portsmouth/logo-portsmouth-256.png",
            "Genoa": "https://logodetimes.com/times/genoa/logo-genoa-256.png",
            "Schalke 04": "https://logodetimes.com/times/schalke-04/logo-schalke-04-256.png",
            "Las Palmas": "https://logodetimes.com/times/las-palmas/logo-las-palmas-256.png",
            "Sassuolo": "https://logodetimes.com/times/sassuolo/logo-sassuolo-256.png",
            "Zenit": "https://logodetimes.com/times/zenit/logo-zenit-256.png",
            "Estrela Vermelha": "https://logodetimes.com/times/estrela-vermelha/logo-estrela-vermelha-256.png",
            "Racing": "https://logodetimes.com/times/racing-club/logo-racing-club-256.png",
            "Olympiacos": "https://logodetimes.com/times/olympiacos/logo-olympiacos-256.png",
            "AEK": "https://logodetimes.com/times/aek-atenas/logo-aek-atenas-256.png",
            "Benfica": "https://logodetimes.com/times/benfica/logo-benfica-256.png",
        }

        clubes = Clube.objects.all()
        faltantes = [c for c in clubes if not c.escudo]

        self.stdout.write(self.style.WARNING(f"\nResgatando {len(faltantes)} clubes..."))

        sucessos = 0
        falhas = 0

        for clube in faltantes:

            if clube.nome in urls_corrigidas:
                url = urls_corrigidas[clube.nome]
            else:
                slug = self.normalizar_nome(clube.nome)
                url = f"https://logodetimes.com/times/{slug}/logo-{slug}-256.png"

            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                resposta = requests.get(url, timeout=10, headers=headers)

                if resposta.status_code == 200 and "image" in resposta.headers.get("Content-Type", ""):

                    nome_arquivo = f"{self.normalizar_nome(clube.nome)}.png"
                    clube.escudo.save(nome_arquivo, ContentFile(resposta.content), save=True)

                    self.stdout.write(self.style.SUCCESS(f'[+] {clube.nome} OK'))
                    sucessos += 1
                else:
                    self.stdout.write(self.style.ERROR(f'[X] {clube.nome} falhou'))
                    falhas += 1

            except:
                self.stdout.write(self.style.ERROR(f'[X] erro rede: {clube.nome}'))
                falhas += 1

        self.stdout.write(self.style.WARNING(f"\nFINAL: {sucessos} OK | {falhas} falhas"))
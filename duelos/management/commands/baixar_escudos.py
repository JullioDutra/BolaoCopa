import requests
import unicodedata
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from duelos.models import Clube

class Command(BaseCommand):
    help = 'Baixa os escudos via Wikipedia (Site permitido pelo PythonAnywhere)'

    def normalizar_nome(self, nome):
        nome_sem_acentos = ''.join(c for c in unicodedata.normalize('NFD', nome) if unicodedata.category(c) != 'Mn')
        return nome_sem_acentos.lower().replace(' ', '_')

    def handle(self, *args, **kwargs):
        # Dicionário GIGANTE apenas com a Wikipedia (Permitida pelo firewall do PythonAnywhere)
        urls_permitidas = {
            # --- BRASILEIROS ---
            "Flamengo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Flamengo_braz_logo.svg/256px-Flamengo_braz_logo.svg.png",
            "Vasco": "https://upload.wikimedia.org/wikipedia/pt/thumb/a/ac/CRVascodaGama.png/256px-CRVascodaGama.png",
            "Palmeiras": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Palmeiras_logo.svg/256px-Palmeiras_logo.svg.png",
            "Corinthians": "https://upload.wikimedia.org/wikipedia/pt/thumb/b/b4/Corinthians_simbolo.png/256px-Corinthians_simbolo.png",
            "São Paulo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/S%C3%A3o_Paulo_Futebol_Clube.png/256px-S%C3%A3o_Paulo_Futebol_Clube.png",
            "Santos": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Santos_Logo.png/256px-Santos_Logo.png",
            "Cruzeiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Cruzeiro_Esporte_Clube_%28logo%29.svg/256px-Cruzeiro_Esporte_Clube_%28logo%29.svg.png",
            "Atlético Mineiro": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Atletico_mineiro_galo.png/256px-Atletico_mineiro_galo.png",
            "Grêmio": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Shield_of_Gr%C3%AAmio_Foot-Ball_Porto_Alegrense.svg/256px-Shield_of_Gr%C3%AAmio_Foot-Ball_Porto_Alegrense.svg.png",
            "Internacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Escudo_do_Sport_Club_Internacional.svg/256px-Escudo_do_Sport_Club_Internacional.svg.png",
            "Fluminense": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Escudo_do_Fluminense.svg/256px-Escudo_do_Fluminense.svg.png",
            "Botafogo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Escudo_Botafogo.svg/256px-Escudo_Botafogo.svg.png",
            "Athletico Paranaense": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/CA_Athletico_Paranaense.svg/256px-CA_Athletico_Paranaense.svg.png",
            "Coritiba": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Coritiba_FBC_logo.svg/256px-Coritiba_FBC_logo.svg.png",
            "Goiás": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Goi%C3%A1s_Esporte_Clube_logo.svg/256px-Goi%C3%A1s_Esporte_Clube_logo.svg.png",
            "Vitória": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Escudo_do_Esporte_Clube_Vit%C3%B3ria.svg/256px-Escudo_do_Esporte_Clube_Vit%C3%B3ria.svg.png",
            "São Caetano": "https://upload.wikimedia.org/wikipedia/pt/thumb/e/e7/AD_S%C3%A3o_Caetano.png/256px-AD_S%C3%A3o_Caetano.png",

            # --- EUROPEUS ---
            "Real Madrid": "https://upload.wikimedia.org/wikipedia/pt/9/98/Real_Madrid.png",
            "Barcelona": "https://upload.wikimedia.org/wikipedia/pt/thumb/4/43/FCBarcelona.svg/256px-FCBarcelona.svg.png",
            "Milan": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/256px-Logo_of_AC_Milan.svg.png",
            "Inter de Milão": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FC_Internazionale_Milano_2021.svg/256px-FC_Internazionale_Milano_2021.svg.png",
            "Juventus": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Juventus_FC_2017_icon_%28black%29.svg/256px-Juventus_FC_2017_icon_%28black%29.svg.png",
            "Chelsea": "https://upload.wikimedia.org/wikipedia/pt/thumb/c/cc/Chelsea_FC.svg/256px-Chelsea_FC.svg.png",
            "Manchester United": "https://upload.wikimedia.org/wikipedia/pt/thumb/4/43/Manchester_United_FC.svg/256px-Manchester_United_FC.svg.png",
            "Bayern de Munique": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg/256px-FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg.png",
            "PSG": "https://upload.wikimedia.org/wikipedia/pt/thumb/a/a2/Paris_Saint-Germain_Football_Club.svg/256px-Paris_Saint-Germain_Football_Club.svg.png",
            "Arsenal": "https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/256px-Arsenal_FC.svg.png",
            "Liverpool": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/256px-Liverpool_FC.svg.png",
            "Manchester City": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/256px-Manchester_City_FC_badge.svg.png",
            "Tottenham": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Tottenham_Hotspur.svg/256px-Tottenham_Hotspur.svg.png",
            "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/256px-Borussia_Dortmund_logo.svg.png",
            "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/thumb/5/59/Bayer_04_Leverkusen_logo.svg/256px-Bayer_04_Leverkusen_logo.svg.png",
            "Atlético de Madrid": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f4/Atletico_Madrid_2017_logo.svg/256px-Atletico_Madrid_2017_logo.svg.png",
            "Ajax": "https://upload.wikimedia.org/wikipedia/en/thumb/7/79/Ajax_Amsterdam.svg/256px-Ajax_Amsterdam.svg.png",
            "PSV": "https://upload.wikimedia.org/wikipedia/en/thumb/0/05/PSV_Eindhoven.svg/256px-PSV_Eindhoven.svg.png",
            "Porto": "https://upload.wikimedia.org/wikipedia/pt/thumb/f/f1/FC_Porto.svg/256px-FC_Porto.svg.png",
            "Benfica": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/SL_Benfica_logo.svg/256px-SL_Benfica_logo.svg.png",
            "Sporting": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e2/Sporting_CP_logo.svg/256px-Sporting_CP_logo.svg.png",

            # --- SUL-AMERICANOS ---
            "Boca Juniors": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Escudo_de_Boca_Juniors.svg/256px-Escudo_de_Boca_Juniors.svg.png",
            "River Plate": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Logo_River_Plate_2022.svg/256px-Logo_River_Plate_2022.svg.png",
            "San Lorenzo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg/256px-Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg.png",
            "Racing": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Escudo_de_Racing_Club_%282014%29.svg/256px-Escudo_de_Racing_Club_%282014%29.svg.png",
            "Nacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Club_Nacional_de_Football_-_Uruguay.svg/256px-Club_Nacional_de_Football_-_Uruguay.svg.png",
            "Colo-Colo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/11/Colo-Colo_logo.svg/256px-Colo-Colo_logo.svg.png"
        }

        clubes = Clube.objects.all()
        sucessos = 0
        falhas = 0

        self.stdout.write(self.style.WARNING(f"\nBaixando via Wikipedia para fintar o firewall do PythonAnywhere..."))

        for clube in clubes:
            if clube.escudo:
                continue

            # Se o clube estiver na nossa lista permitida, tentamos baixar
            if clube.nome in urls_permitidas:
                url = urls_permitidas[clube.nome]
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    resposta = requests.get(url, stream=True, headers=headers, timeout=10)
                    
                    if resposta.status_code == 200:
                        nome_arquivo = f"{self.normalizar_nome(clube.nome)}.png"
                        clube.escudo.save(nome_arquivo, ContentFile(resposta.content), save=True)
                        self.stdout.write(self.style.SUCCESS(f'[+] {clube.nome} descarregado com sucesso da Wikipedia!'))
                        sucessos += 1
                    else:
                        self.stdout.write(self.style.ERROR(f'[X] {clube.nome} não encontrado.'))
                        falhas += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'[X] Erro no {clube.nome}.'))
                    falhas += 1
            else:
                self.stdout.write(self.style.NOTICE(f'[-] {clube.nome} não tem link da Wikipedia mapeado. Adicione via /admin.'))
                falhas += 1

        self.stdout.write(self.style.WARNING(f"\nFim! {sucessos} escudos baixados. Os restantes ({falhas}) terão de ser adicionados via painel /admin."))
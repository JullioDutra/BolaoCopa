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
            # GIGANTES EUROPEUS (Convertidos para PNG)
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
            "Roma": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/AS_Roma_logo_%282017%29.svg/256px-AS_Roma_logo_%282017%29.svg.png",
            "Napoli": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/S.S.C._Napoli_logo.svg/256px-S.S.C._Napoli_logo.svg.png",
            "Lazio": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e4/SS_Lazio.svg/256px-SS_Lazio.svg.png",
            "Fiorentina": "https://upload.wikimedia.org/wikipedia/en/thumb/b/ba/ACF_Fiorentina_2.svg/256px-ACF_Fiorentina_2.svg.png",
            "Ajax": "https://upload.wikimedia.org/wikipedia/en/thumb/7/79/Ajax_Amsterdam.svg/256px-Ajax_Amsterdam.svg.png",
            "PSV": "https://upload.wikimedia.org/wikipedia/en/thumb/0/05/PSV_Eindhoven.svg/256px-PSV_Eindhoven.svg.png",
            "Porto": "https://upload.wikimedia.org/wikipedia/pt/thumb/f/f1/FC_Porto.svg/256px-FC_Porto.svg.png",
            "Benfica": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/SL_Benfica_logo.svg/256px-SL_Benfica_logo.svg.png",
            "Sporting": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e2/Sporting_CP_logo.svg/256px-Sporting_CP_logo.svg.png",

            # GIGANTES SUL-AMERICANOS E OUTROS
            "Boca Juniors": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Escudo_de_Boca_Juniors.svg/256px-Escudo_de_Boca_Juniors.svg.png",
            "River Plate": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Logo_River_Plate_2022.svg/256px-Logo_River_Plate_2022.svg.png",
            "San Lorenzo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg/256px-Escudo_del_Club_Atl%C3%A9tico_San_Lorenzo_de_Almagro.svg.png",
            "Racing": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Escudo_de_Racing_Club_%282014%29.svg/256px-Escudo_de_Racing_Club_%282014%29.svg.png",
            "Estudiantes": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Escudo_de_Estudiantes_de_La_Plata.svg/256px-Escudo_de_Estudiantes_de_La_Plata.svg.png",
            "Nacional": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Club_Nacional_de_Football_-_Uruguay.svg/256px-Club_Nacional_de_Football_-_Uruguay.svg.png",
            "Colo-Colo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/11/Colo-Colo_logo.svg/256px-Colo-Colo_logo.svg.png",
            "LDU": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/LDU_logo.svg/256px-LDU_logo.svg.png",
            
            # EQUIPAS RARAS DA TRAJETÓRIA
            "Galatasaray": "https://upload.wikimedia.org/wikipedia/commons/f/f6/Galatasaray_Sports_Club_Logo.png",
            "Fenerbahçe": "https://upload.wikimedia.org/wikipedia/en/thumb/3/39/Fenerbah%C3%A7e.svg/256px-Fenerbah%C3%A7e.svg.png",
            "Besiktas": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Be%C5%9Fikta%C5%9F_logo.svg/256px-Be%C5%9Fikta%C5%9F_logo.svg.png",
            "Zenit": "https://upload.wikimedia.org/wikipedia/en/0/00/FC_Zenit_1_star_2015_logo.png",
            "LA Galaxy": "https://upload.wikimedia.org/wikipedia/en/thumb/6/62/LA_Galaxy_logo_%282024%29.svg/256px-LA_Galaxy_logo_%282024%29.svg.png",
            "Orlando City": "https://upload.wikimedia.org/wikipedia/en/thumb/2/23/Orlando_City_SC_%282014%29.svg/256px-Orlando_City_SC_%282014%29.svg.png",
            "Kashima Antlers": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cb/Kashima_Antlers_logo.svg/256px-Kashima_Antlers_logo.svg.png"
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
                self.stdout.write(self.style.ERROR(f'[X] Erro de rede ao baixar {clube.nome}'))
                falhas += 1

        self.stdout.write(self.style.WARNING(f"\nResumo: {sucessos} PNGs adicionados com sucesso | {falhas} falharam."))
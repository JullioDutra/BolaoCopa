import requests
from io import BytesIO
from PIL import Image, ImageDraw

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from minijogo.models import EsquadraoHistorico


class Command(BaseCommand):
    help = 'Popula o banco de dados com Esquadrões Históricos, busca escudos na Wikipedia e cria fallbacks.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sem-escudos',
            action='store_true',
            help='Pula a busca de escudos na Wikipedia (mais rápido, útil para testes).',
        )

    # Dicionário expandido para cobrir praticamente todos os grandes e médios do Brasil
    WIKI_TITULOS = {
        "Atlético-MG": "Clube_Atlético_Mineiro",
        "Cruzeiro": "Cruzeiro_Esporte_Clube",
        "Flamengo": "Clube_de_Regatas_do_Flamengo",
        "Palmeiras": "Sociedade_Esportiva_Palmeiras",
        "São Paulo": "São_Paulo_Futebol_Clube",
        "Vasco da Gama": "Club_de_Regatas_Vasco_da_Gama",
        "Santos": "Santos_Futebol_Clube",
        "Corinthians": "Sport_Club_Corinthians_Paulista",
        "Grêmio": "Grêmio_Foot-Ball_Porto_Alegrense",
        "Fluminense": "Fluminense_Football_Club",
        "Botafogo": "Botafogo_de_Futebol_e_Regatas",
        "Internacional": "Sport_Club_Internacional",
        "Bahia": "Esporte_Clube_Bahia",
        "Vitória": "Esporte_Clube_Vitória",
        "Sport Recife": "Sport_Club_do_Recife",
        "Náutico": "Clube_Náutico_Capibaribe",
        "Santa Cruz": "Santa_Cruz_Futebol_Clube",
        "Coritiba": "Coritiba_Foot_Ball_Club",
        "Athletico Paranaense": "Club_Athletico_Paranaense",
        "Ceará": "Ceará_Sporting_Club",
        "Fortaleza": "Fortaleza_Esporte_Clube",
        "Goiás": "Goiás_Esporte_Clube",
        "Paysandu": "Paysandu_Sport_Club",
        "Chapecoense": "Associação_Chapecoense_de_Futebol",
        "Ponte Preta": "Associação_Atlética_Ponte_Preta",
        "Guarani": "Guarani_Futebol_Clube",
        "Paulista": "Paulista_Futebol_Clube",
        "Santo André": "Esporte_Clube_Santo_André"
    }

    esquadroes_data = [
        # --- ERA 2020+ ---
        {"nome": "Fluminense 2023", "clube": "Fluminense", "ano": 2023, "gols_pro": 115, "gols_sofridos": 66, "titulos": 2}, # Liberta e Carioca
        {"nome": "Palmeiras 2022", "clube": "Palmeiras", "ano": 2022, "gols_pro": 142, "gols_sofridos": 50, "titulos": 3}, # BR, Paulista, Recopa
        {"nome": "Flamengo 2022", "clube": "Flamengo", "ano": 2022, "gols_pro": 138, "gols_sofridos": 65, "titulos": 2}, # Liberta, CdB
        {"nome": "Atlético-MG 2021", "clube": "Atlético-MG", "ano": 2021, "gols_pro": 136, "gols_sofridos": 52, "titulos": 3}, # BR, CdB, Mineiro
        {"nome": "Palmeiras 2020", "clube": "Palmeiras", "ano": 2020, "gols_pro": 122, "gols_sofridos": 56, "titulos": 3}, # Liberta, CdB, Paulista
        {"nome": "Flamengo 2020", "clube": "Flamengo", "ano": 2020, "gols_pro": 138, "gols_sofridos": 63, "titulos": 4}, # BR, Recopa, Supercopa, Carioca
        
        # --- ANOS 2010 ---
        {"nome": "Flamengo 2019", "clube": "Flamengo", "ano": 2019, "gols_pro": 150, "gols_sofridos": 64, "titulos": 3}, # Liberta, BR, Carioca
        {"nome": "Athletico-PR 2019", "clube": "Athletico Paranaense", "ano": 2019, "gols_pro": 95, "gols_sofridos": 47, "titulos": 2}, # CdB, Paranaense
        {"nome": "Palmeiras 2018", "clube": "Palmeiras", "ano": 2018, "gols_pro": 120, "gols_sofridos": 50, "titulos": 1}, # BR
        {"nome": "Grêmio 2017", "clube": "Grêmio", "ano": 2017, "gols_pro": 118, "gols_sofridos": 61, "titulos": 1}, # Liberta
        {"nome": "Corinthians 2017", "clube": "Corinthians", "ano": 2017, "gols_pro": 90, "gols_sofridos": 46, "titulos": 2}, # BR, Paulista
        {"nome": "Chapecoense 2016", "clube": "Chapecoense", "ano": 2016, "gols_pro": 92, "gols_sofridos": 74, "titulos": 2}, # Sul-Americana, Catarinense
        {"nome": "Corinthians 2015", "clube": "Corinthians", "ano": 2015, "gols_pro": 110, "gols_sofridos": 49, "titulos": 1}, # BR
        {"nome": "Cruzeiro 2014", "clube": "Cruzeiro", "ano": 2014, "gols_pro": 118, "gols_sofridos": 55, "titulos": 2}, # BR, Mineiro
        {"nome": "Cruzeiro 2013", "clube": "Cruzeiro", "ano": 2013, "gols_pro": 116, "gols_sofridos": 50, "titulos": 1}, # BR
        {"nome": "Atlético-MG 2013", "clube": "Atlético-MG", "ano": 2013, "gols_pro": 125, "gols_sofridos": 69, "titulos": 2}, # Liberta, Mineiro
        {"nome": "Corinthians 2012", "clube": "Corinthians", "ano": 2012, "gols_pro": 89, "gols_sofridos": 47, "titulos": 2}, # Mundial, Liberta
        {"nome": "Fluminense 2012", "clube": "Fluminense", "ano": 2012, "gols_pro": 105, "gols_sofridos": 58, "titulos": 2}, # BR, Carioca
        {"nome": "Santos 2011", "clube": "Santos", "ano": 2011, "gols_pro": 128, "gols_sofridos": 75, "titulos": 2}, # Liberta, Paulista
        {"nome": "Santos 2010", "clube": "Santos", "ano": 2010, "gols_pro": 176, "gols_sofridos": 93, "titulos": 2}, # CdB, Paulista
        {"nome": "Internacional 2010", "clube": "Internacional", "ano": 2010, "gols_pro": 110, "gols_sofridos": 55, "titulos": 1}, # Liberta

        # --- ANOS 2000 ---
        {"nome": "São Paulo 2008", "clube": "São Paulo", "ano": 2008, "gols_pro": 98, "gols_sofridos": 55, "titulos": 1}, # BR
        {"nome": "Sport 2008", "clube": "Sport Recife", "ano": 2008, "gols_pro": 110, "gols_sofridos": 60, "titulos": 2}, # CdB, Pernambucano
        {"nome": "São Paulo 2006", "clube": "São Paulo", "ano": 2006, "gols_pro": 115, "gols_sofridos": 60, "titulos": 1}, # BR
        {"nome": "Internacional 2006", "clube": "Internacional", "ano": 2006, "gols_pro": 105, "gols_sofridos": 55, "titulos": 2}, # Mundial, Liberta
        {"nome": "São Paulo 2005", "clube": "São Paulo", "ano": 2005, "gols_pro": 166, "gols_sofridos": 89, "titulos": 3}, # Mundial, Liberta, Paulista
        {"nome": "Paulista 2005", "clube": "Paulista", "ano": 2005, "gols_pro": 65, "gols_sofridos": 40, "titulos": 1}, # CdB
        {"nome": "Santo André 2004", "clube": "Santo André", "ano": 2004, "gols_pro": 70, "gols_sofridos": 42, "titulos": 1}, # CdB
        {"nome": "Cruzeiro 2003", "clube": "Cruzeiro", "ano": 2003, "gols_pro": 179, "gols_sofridos": 75, "titulos": 3}, # Tríplice Coroa
        {"nome": "Santos 2002", "clube": "Santos", "ano": 2002, "gols_pro": 121, "gols_sofridos": 61, "titulos": 1}, # BR
        {"nome": "Paysandu 2002", "clube": "Paysandu", "ano": 2002, "gols_pro": 85, "gols_sofridos": 45, "titulos": 2}, # Copa dos Campeões, Paraense
        {"nome": "Athletico-PR 2001", "clube": "Athletico Paranaense", "ano": 2001, "gols_pro": 108, "gols_sofridos": 55, "titulos": 2}, # BR, Paranaense
        {"nome": "Grêmio 2001", "clube": "Grêmio", "ano": 2001, "gols_pro": 100, "gols_sofridos": 50, "titulos": 2}, # CdB, Gauchão
        {"nome": "Vasco 2000", "clube": "Vasco da Gama", "ano": 2000, "gols_pro": 135, "gols_sofridos": 70, "titulos": 2}, # BR, Mercosul
        {"nome": "Corinthians 2000", "clube": "Corinthians", "ano": 2000, "gols_pro": 115, "gols_sofridos": 65, "titulos": 1}, # Mundial
        {"nome": "Goiás 2000", "clube": "Goiás", "ano": 2000, "gols_pro": 88, "gols_sofridos": 52, "titulos": 2}, # Centro-Oeste, Goiano

        # --- ANOS 90 ---
        {"nome": "Palmeiras 1999", "clube": "Palmeiras", "ano": 1999, "gols_pro": 164, "gols_sofridos": 88, "titulos": 1}, # Liberta
        {"nome": "Corinthians 1999", "clube": "Corinthians", "ano": 1999, "gols_pro": 130, "gols_sofridos": 65, "titulos": 2}, # BR, Paulista
        {"nome": "Vasco 1998", "clube": "Vasco da Gama", "ano": 1998, "gols_pro": 115, "gols_sofridos": 65, "titulos": 2}, # Liberta, Carioca
        {"nome": "Vasco 1997", "clube": "Vasco da Gama", "ano": 1997, "gols_pro": 110, "gols_sofridos": 55, "titulos": 1}, # BR
        {"nome": "Grêmio 1995", "clube": "Grêmio", "ano": 1995, "gols_pro": 102, "gols_sofridos": 44, "titulos": 2}, # Liberta, Gauchão
        {"nome": "Botafogo 1995", "clube": "Botafogo", "ano": 1995, "gols_pro": 98, "gols_sofridos": 52, "titulos": 1}, # BR
        {"nome": "Palmeiras 1993", "clube": "Palmeiras", "ano": 1993, "gols_pro": 140, "gols_sofridos": 55, "titulos": 3}, # BR, Paulista, Rio-SP
        {"nome": "São Paulo 1993", "clube": "São Paulo", "ano": 1993, "gols_pro": 135, "gols_sofridos": 60, "titulos": 3}, # Mundial, Liberta, Recopa
        {"nome": "São Paulo 1992", "clube": "São Paulo", "ano": 1992, "gols_pro": 125, "gols_sofridos": 55, "titulos": 3}, # Mundial, Liberta, Paulista
        {"nome": "Corinthians 1990", "clube": "Corinthians", "ano": 1990, "gols_pro": 78, "gols_sofridos": 30, "titulos": 1}, # BR
        {"nome": "Ponte Preta 1990", "clube": "Ponte Preta", "ano": 1990, "gols_pro": 60, "gols_sofridos": 35, "titulos": 0}, 

        # --- LENDÁRIOS CLÁSSICOS ---
        {"nome": "Bahia 1988", "clube": "Bahia", "ano": 1988, "gols_pro": 87, "gols_sofridos": 41, "titulos": 2}, # BR, Baiano
        {"nome": "Sport 1987", "clube": "Sport Recife", "ano": 1987, "gols_pro": 90, "gols_sofridos": 45, "titulos": 1}, # BR
        {"nome": "São Paulo 1986", "clube": "São Paulo", "ano": 1986, "gols_pro": 95, "gols_sofridos": 40, "titulos": 1}, # BR
        {"nome": "Coritiba 1985", "clube": "Coritiba", "ano": 1985, "gols_pro": 80, "gols_sofridos": 38, "titulos": 1}, # BR
        {"nome": "Fluminense 1984", "clube": "Fluminense", "ano": 1984, "gols_pro": 85, "gols_sofridos": 35, "titulos": 2}, # BR, Carioca
        {"nome": "Grêmio 1983", "clube": "Grêmio", "ano": 1983, "gols_pro": 95, "gols_sofridos": 40, "titulos": 2}, # Mundial, Liberta
        {"nome": "Flamengo 1981", "clube": "Flamengo", "ano": 1981, "gols_pro": 140, "gols_sofridos": 50, "titulos": 3}, # Mundial, Liberta, Carioca
        {"nome": "Internacional 1979", "clube": "Internacional", "ano": 1979, "gols_pro": 90, "gols_sofridos": 30, "titulos": 1}, # BR Invicto
        {"nome": "Guarani 1978", "clube": "Guarani", "ano": 1978, "gols_pro": 70, "gols_sofridos": 33, "titulos": 1}, # BR
        {"nome": "Santos 1962", "clube": "Santos", "ano": 1962, "gols_pro": 216, "gols_sofridos": 87, "titulos": 4}, # Mundial, Liberta, Taça BR, Paulista
    ]

    def gerar_escudo_padrao(self, esquadrao):
        """Desenha um escudo circular estilizado para o clube se não houver foto."""
        img = Image.new('RGBA', (300, 300), color=(255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Fundo do escudo (Cinza escuro/Chumbo)
        box = (10, 10, 290, 290)
        draw.ellipse(box, fill=(44, 62, 80), outline=(241, 196, 15), width=8)

        # Letras do clube (ex: "Flamengo" -> "FLA")
        partes = esquadrao.clube.split()
        iniciais = partes[0][0:3].upper() if len(partes) == 1 else f"{partes[0][0]}{partes[1][0]}"

        draw.text((150, 120), iniciais, fill=(241, 196, 15), align="center", anchor="mm")
        draw.text((150, 180), f"{esquadrao.ano}", fill=(255, 255, 255), align="center", anchor="mm")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        nome_arquivo = f"escudo_gen_{esquadrao.clube.replace(' ', '_').lower()}.png"
        esquadrao.escudo.save(nome_arquivo, ContentFile(buffer.getvalue()), save=True)


    def buscar_escudo(self, clube):
        """Busca a imagem de resumo da página do clube na Wikipedia (pt) e devolve os bytes."""
        titulo = self.WIKI_TITULOS.get(clube)
        if not titulo:
            return None

        url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{titulo}"
        try:
            resp = requests.get(url, timeout=8, headers={"User-Agent": "MinijogoEsquadroesBot/1.0"})
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException:
            return None

        thumbnail = data.get("thumbnail") or data.get("originalimage")
        if not thumbnail or not thumbnail.get("source"):
            return None

        img_url = thumbnail["source"]
        try:
            img_resp = requests.get(img_url, timeout=8, headers={"User-Agent": "MinijogoEsquadroesBot/1.0"})
            img_resp.raise_for_status()
        except requests.RequestException:
            return None

        return img_resp.content, img_url

    def handle(self, *args, **kwargs):
        buscar_escudos = not kwargs.get('sem_escudos')
        criados = 0
        atualizados = 0
        escudos_baixados = 0
        escudos_desenhados = 0

        for dados in self.esquadroes_data:
            obj, created = EsquadraoHistorico.objects.update_or_create(
                nome=dados['nome'],
                defaults={
                    'clube': dados['clube'],
                    'ano': dados['ano'],
                    'gols_pro': dados['gols_pro'],
                    'gols_sofridos': dados['gols_sofridos'],
                    'titulos': dados['titulos'],
                    'ativo': True,
                }
            )

            if created:
                criados += 1
                self.stdout.write(self.style.SUCCESS(f'  + Criado: {obj.nome}'))
            else:
                atualizados += 1
                self.stdout.write(self.style.WARNING(f'  ~ Atualizado: {obj.nome}'))

            # Tenta baixar o escudo
            if buscar_escudos and not obj.escudo:
                resultado = self.buscar_escudo(dados['clube'])
                if resultado:
                    conteudo, img_url = resultado
                    nome_arquivo = f"{dados['clube'].replace(' ', '_')}.png"
                    obj.escudo.save(nome_arquivo, ContentFile(conteudo), save=True)
                    escudos_baixados += 1
                    self.stdout.write(self.style.SUCCESS(f'    ↳ Escudo salvo da Wiki'))
                else:
                    # FALLBACK: Se não achar na Wiki, desenha um escudo genérico!
                    self.gerar_escudo_padrao(obj)
                    escudos_desenhados += 1
                    self.stdout.write(self.style.WARNING(f'    ↳ Escudo desenhado manualmente para {dados["clube"]}'))

        total = criados + atualizados
        self.stdout.write(self.style.SUCCESS(
            f'\nConcluído! {total} esquadrões processados '
            f'({criados} criados, {atualizados} atualizados, {escudos_baixados} escudos baixados, {escudos_desenhados} escudos desenhados).'
        ))

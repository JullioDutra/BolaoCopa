from django.core.files import File
from django.core.management.base import BaseCommand

from minijogo.models import EsquadraoHistorico
# Importando o seu modelo de clubes do app duelos
from duelos.models import Clube 

class Command(BaseCommand):
    help = 'Popula os Esquadrões Históricos e puxa os escudos EXCLUSIVAMENTE do banco local (duelos.Clube).'

    esquadroes_data = [
        # --- ERA 2020+ ---
        {"nome": "Fluminense 2023", "clube": "Fluminense", "ano": 2023, "gols_pro": 115, "gols_sofridos": 66, "titulos": 2}, 
        {"nome": "Palmeiras 2022", "clube": "Palmeiras", "ano": 2022, "gols_pro": 142, "gols_sofridos": 50, "titulos": 3}, 
        {"nome": "Flamengo 2022", "clube": "Flamengo", "ano": 2022, "gols_pro": 138, "gols_sofridos": 65, "titulos": 2}, 
        {"nome": "Atlético-MG 2021", "clube": "Atlético-MG", "ano": 2021, "gols_pro": 136, "gols_sofridos": 52, "titulos": 3}, 
        {"nome": "Palmeiras 2020", "clube": "Palmeiras", "ano": 2020, "gols_pro": 122, "gols_sofridos": 56, "titulos": 3}, 
        {"nome": "Flamengo 2020", "clube": "Flamengo", "ano": 2020, "gols_pro": 138, "gols_sofridos": 63, "titulos": 4}, 
        
        # --- ANOS 2010 ---
        {"nome": "Flamengo 2019", "clube": "Flamengo", "ano": 2019, "gols_pro": 150, "gols_sofridos": 64, "titulos": 3}, 
        {"nome": "Athletico-PR 2019", "clube": "Athletico Paranaense", "ano": 2019, "gols_pro": 95, "gols_sofridos": 47, "titulos": 2}, 
        {"nome": "Palmeiras 2018", "clube": "Palmeiras", "ano": 2018, "gols_pro": 120, "gols_sofridos": 50, "titulos": 1}, 
        {"nome": "Grêmio 2017", "clube": "Grêmio", "ano": 2017, "gols_pro": 118, "gols_sofridos": 61, "titulos": 1}, 
        {"nome": "Corinthians 2017", "clube": "Corinthians", "ano": 2017, "gols_pro": 90, "gols_sofridos": 46, "titulos": 2}, 
        {"nome": "Chapecoense 2016", "clube": "Chapecoense", "ano": 2016, "gols_pro": 92, "gols_sofridos": 74, "titulos": 2}, 
        {"nome": "Corinthians 2015", "clube": "Corinthians", "ano": 2015, "gols_pro": 110, "gols_sofridos": 49, "titulos": 1}, 
        {"nome": "Cruzeiro 2014", "clube": "Cruzeiro", "ano": 2014, "gols_pro": 118, "gols_sofridos": 55, "titulos": 2}, 
        {"nome": "Cruzeiro 2013", "clube": "Cruzeiro", "ano": 2013, "gols_pro": 116, "gols_sofridos": 50, "titulos": 1}, 
        {"nome": "Atlético-MG 2013", "clube": "Atlético-MG", "ano": 2013, "gols_pro": 125, "gols_sofridos": 69, "titulos": 2}, 
        {"nome": "Corinthians 2012", "clube": "Corinthians", "ano": 2012, "gols_pro": 89, "gols_sofridos": 47, "titulos": 2}, 
        {"nome": "Fluminense 2012", "clube": "Fluminense", "ano": 2012, "gols_pro": 105, "gols_sofridos": 58, "titulos": 2}, 
        {"nome": "Santos 2011", "clube": "Santos", "ano": 2011, "gols_pro": 128, "gols_sofridos": 75, "titulos": 2}, 
        {"nome": "Santos 2010", "clube": "Santos", "ano": 2010, "gols_pro": 176, "gols_sofridos": 93, "titulos": 2}, 
        {"nome": "Internacional 2010", "clube": "Internacional", "ano": 2010, "gols_pro": 110, "gols_sofridos": 55, "titulos": 1}, 

        # --- ANOS 2000 ---
        {"nome": "São Paulo 2008", "clube": "São Paulo", "ano": 2008, "gols_pro": 98, "gols_sofridos": 55, "titulos": 1}, 
        {"nome": "Sport 2008", "clube": "Sport Recife", "ano": 2008, "gols_pro": 110, "gols_sofridos": 60, "titulos": 2}, 
        {"nome": "São Paulo 2006", "clube": "São Paulo", "ano": 2006, "gols_pro": 115, "gols_sofridos": 60, "titulos": 1}, 
        {"nome": "Internacional 2006", "clube": "Internacional", "ano": 2006, "gols_pro": 105, "gols_sofridos": 55, "titulos": 2}, 
        {"nome": "São Paulo 2005", "clube": "São Paulo", "ano": 2005, "gols_pro": 166, "gols_sofridos": 89, "titulos": 3}, 
        {"nome": "Paulista 2005", "clube": "Paulista", "ano": 2005, "gols_pro": 65, "gols_sofridos": 40, "titulos": 1}, 
        {"nome": "Santo André 2004", "clube": "Santo André", "ano": 2004, "gols_pro": 70, "gols_sofridos": 42, "titulos": 1}, 
        {"nome": "Cruzeiro 2003", "clube": "Cruzeiro", "ano": 2003, "gols_pro": 179, "gols_sofridos": 75, "titulos": 3}, 
        {"nome": "Santos 2002", "clube": "Santos", "ano": 2002, "gols_pro": 121, "gols_sofridos": 61, "titulos": 1}, 
        {"nome": "Paysandu 2002", "clube": "Paysandu", "ano": 2002, "gols_pro": 85, "gols_sofridos": 45, "titulos": 2}, 
        {"nome": "Athletico-PR 2001", "clube": "Athletico Paranaense", "ano": 2001, "gols_pro": 108, "gols_sofridos": 55, "titulos": 2}, 
        {"nome": "Grêmio 2001", "clube": "Grêmio", "ano": 2001, "gols_pro": 100, "gols_sofridos": 50, "titulos": 2}, 
        {"nome": "Vasco 2000", "clube": "Vasco da Gama", "ano": 2000, "gols_pro": 135, "gols_sofridos": 70, "titulos": 2}, 
        {"nome": "Corinthians 2000", "clube": "Corinthians", "ano": 2000, "gols_pro": 115, "gols_sofridos": 65, "titulos": 1}, 
        {"nome": "Goiás 2000", "clube": "Goiás", "ano": 2000, "gols_pro": 88, "gols_sofridos": 52, "titulos": 2}, 

        # --- ANOS 90 ---
        {"nome": "Palmeiras 1999", "clube": "Palmeiras", "ano": 1999, "gols_pro": 164, "gols_sofridos": 88, "titulos": 1}, 
        {"nome": "Corinthians 1999", "clube": "Corinthians", "ano": 1999, "gols_pro": 130, "gols_sofridos": 65, "titulos": 2}, 
        {"nome": "Vasco 1998", "clube": "Vasco da Gama", "ano": 1998, "gols_pro": 115, "gols_sofridos": 65, "titulos": 2}, 
        {"nome": "Vasco 1997", "clube": "Vasco da Gama", "ano": 1997, "gols_pro": 110, "gols_sofridos": 55, "titulos": 1}, 
        {"nome": "Grêmio 1995", "clube": "Grêmio", "ano": 1995, "gols_pro": 102, "gols_sofridos": 44, "titulos": 2}, 
        {"nome": "Botafogo 1995", "clube": "Botafogo", "ano": 1995, "gols_pro": 98, "gols_sofridos": 52, "titulos": 1}, 
        {"nome": "Palmeiras 1993", "clube": "Palmeiras", "ano": 1993, "gols_pro": 140, "gols_sofridos": 55, "titulos": 3}, 
        {"nome": "São Paulo 1993", "clube": "São Paulo", "ano": 1993, "gols_pro": 135, "gols_sofridos": 60, "titulos": 3}, 
        {"nome": "São Paulo 1992", "clube": "São Paulo", "ano": 1992, "gols_pro": 125, "gols_sofridos": 55, "titulos": 3}, 
        {"nome": "Corinthians 1990", "clube": "Corinthians", "ano": 1990, "gols_pro": 78, "gols_sofridos": 30, "titulos": 1}, 
        {"nome": "Ponte Preta 1990", "clube": "Ponte Preta", "ano": 1990, "gols_pro": 60, "gols_sofridos": 35, "titulos": 0}, 

        # --- LENDÁRIOS CLÁSSICOS ---
        {"nome": "Bahia 1988", "clube": "Bahia", "ano": 1988, "gols_pro": 87, "gols_sofridos": 41, "titulos": 2}, 
        {"nome": "Sport 1987", "clube": "Sport Recife", "ano": 1987, "gols_pro": 90, "gols_sofridos": 45, "titulos": 1}, 
        {"nome": "São Paulo 1986", "clube": "São Paulo", "ano": 1986, "gols_pro": 95, "gols_sofridos": 40, "titulos": 1}, 
        {"nome": "Coritiba 1985", "clube": "Coritiba", "ano": 1985, "gols_pro": 80, "gols_sofridos": 38, "titulos": 1}, 
        {"nome": "Fluminense 1984", "clube": "Fluminense", "ano": 1984, "gols_pro": 85, "gols_sofridos": 35, "titulos": 2}, 
        {"nome": "Grêmio 1983", "clube": "Grêmio", "ano": 1983, "gols_pro": 95, "gols_sofridos": 40, "titulos": 2}, 
        {"nome": "Flamengo 1981", "clube": "Flamengo", "ano": 1981, "gols_pro": 140, "gols_sofridos": 50, "titulos": 3}, 
        {"nome": "Internacional 1979", "clube": "Internacional", "ano": 1979, "gols_pro": 90, "gols_sofridos": 30, "titulos": 1}, 
        {"nome": "Guarani 1978", "clube": "Guarani", "ano": 1978, "gols_pro": 70, "gols_sofridos": 33, "titulos": 1}, 
        {"nome": "Santos 1962", "clube": "Santos", "ano": 1962, "gols_pro": 216, "gols_sofridos": 87, "titulos": 4}, 
    ]

    def handle(self, *args, **kwargs):
        criados = 0
        atualizados = 0
        escudos_atualizados = 0
        escudos_sem_imagem = 0

        for dados in self.esquadroes_data:
            # 1. Cria ou atualiza os dados estatísticos do Esquadrão
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
                self.stdout.write(self.style.SUCCESS(f'  + Criado/Processando: {obj.nome}'))
            else:
                atualizados += 1
                self.stdout.write(self.style.WARNING(f'  ~ Atualizando: {obj.nome}'))

            # 2. Busca e ATUALIZA o escudo exclusivamente do banco local
            try:
                # O icontains vai achar "Flamengo" se a busca for "Clube de Regatas do Flamengo", etc.
                time_local = Clube.objects.filter(nome__icontains=dados['clube']).first()
                
                if time_local and time_local.escudo:
                    # Copia a imagem do banco local e substitui a atual do esquadrão
                    with time_local.escudo.open('rb') as arquivo_imagem:
                        # Limpa espaços em branco para salvar arquivo organizado
                        nome_arquivo_local = f"escudo_{dados['clube'].replace(' ', '_').lower()}.png"
                        obj.escudo.save(nome_arquivo_local, File(arquivo_imagem), save=True)
                    
                    escudos_atualizados += 1
                    self.stdout.write(self.style.SUCCESS(f'    ↳ Escudo COPIADO com sucesso! 🚀'))
                else:
                    # Não achou o time ou o time não tem imagem salva
                    escudos_sem_imagem += 1
                    self.stdout.write(self.style.ERROR(f'    ↳ ALERTA: Nenhum escudo encontrado para "{dados["clube"]}"!'))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'    ↳ Erro ao processar escudo: {e}'))

        total = criados + atualizados
        self.stdout.write(self.style.SUCCESS(
            f'\nConcluído! {total} esquadrões atualizados no banco.\n'
            f'Resumo: {escudos_atualizados} escudos importados localmente | {escudos_sem_imagem} times ficaram sem escudo.'
        ))

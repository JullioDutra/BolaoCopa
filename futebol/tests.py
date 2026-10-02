import csv
import json
import os
import tempfile
from datetime import date, timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts import coins
from palpites.models import Clube, Jogo

from . import comparativo as regras
from . import importar, servico
from .models import Atleta, Comparativo, Time, Voto
from .posicoes import mapear_posicao
from .provedores import api_football, espn, football_data, thesportsdb
from .provedores.base import ProvedorIndisponivel


class PosicoesTests(SimpleTestCase):
    def test_mapeia_posicoes_de_varias_fontes(self):
        casos = {
            'Goalkeeper': 'GOL', 'Goleiro': 'GOL', 'G': 'GOL',
            'Centre-Back': 'DEF', 'Left-Back': 'DEF', 'Defence': 'DEF', 'Defender': 'DEF', 'Defensor': 'DEF', 'Zagueiro': 'DEF', 'Lateral-direito': 'DEF',
            'Defensive Midfield': 'MEI', 'Attacking Midfield': 'MEI', 'Midfield': 'MEI', 'Meio-campista': 'MEI', 'Volante': 'MEI',
            'Left Winger': 'ATA', 'Centre-Forward': 'ATA', 'Offence': 'ATA', 'Attacker': 'ATA', 'Atacante': 'ATA', 'Forward': 'ATA',
            '': '', 'Treinador': '',
        }
        for texto, esperado in casos.items():
            self.assertEqual(mapear_posicao(texto), esperado, texto)


def cria_elenco(time, prefixo, goleiros=2, defs=6, meis=5, atas=4):
    n = 1
    for pos, qtd in (('GOL', goleiros), ('DEF', defs), ('MEI', meis), ('ATA', atas)):
        for i in range(qtd):
            Atleta.objects.create(nome=f"{prefixo} {pos}{i + 1}", time=time, posicao=pos, numero=n, overall=60 + (qtd - i) + n % 5)
            n += 1


class ImportacaoTests(TestCase):
    def test_arquivo_csv_e_idempotente(self):
        with tempfile.NamedTemporaryFile('w', suffix='.csv', delete=False, encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['time', 'pais', 'liga', 'jogador', 'posicao', 'numero', 'nascimento', 'nacionalidade', 'overall', 'valor_mercado'])
            w.writerow(['Flamengo', 'Brasil', 'Brasileirão', 'Gabriel Barbosa', 'Atacante', '9', '1996-08-30', 'Brasil', '84', '12000000'])
            w.writerow(['Flamengo', 'Brasil', 'Brasileirão', 'Rossi', 'Goleiro', '1', '', 'Argentina', '80', ''])
            w.writerow(['', '', '', 'sem time', 'Atacante', '', '', '', '', ''])
        try:
            r1 = importar.importar_arquivo(f.name)
            r2 = importar.importar_arquivo(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual((r1['times'], r1['atletas']), (1, 2))
        self.assertEqual((r2['times'], r2['atletas']), (0, 0))
        self.assertEqual(Time.objects.count(), 1)
        gabigol = Atleta.objects.get(nome='Gabriel Barbosa')
        self.assertEqual((gabigol.posicao, gabigol.overall, gabigol.nascimento), ('ATA', 84, date(1996, 8, 30)))

    def test_arquivo_json(self):
        dados = {'times': [{'nome': 'Santos', 'pais': 'Brasil', 'atletas': [{'nome': 'Neymar', 'posicao': 'Left Winger', 'numero': 10}]}]}
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(dados, f)
        try:
            importar.importar_arquivo(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(Atleta.objects.get().posicao, 'ATA')

    def test_internos_aproveita_clube_jogador_e_carta(self):
        from convocacao.models import Jogador
        from duelos.models import CartaTrunfo, ClubeFutebol
        Clube.objects.create(nome='Flamengo', cor_hexadecimal='#C8102E')
        Jogador.objects.create(nome='Pedro', posicao='Atacante', clube_atual='Flamengo')
        Jogador.objects.create(nome='Sem Clube', posicao='Atacante', clube_atual='')
        cf = ClubeFutebol.objects.create(nome='Flamengo')
        CartaTrunfo.objects.create(nome='Pedro', posicao='ATA', overall=85, clube=cf)
        importar.importar_internos()
        importar.importar_internos()
        self.assertEqual(Time.objects.count(), 1)
        t = Time.objects.get()
        self.assertEqual(t.clube_local.nome, 'Flamengo')
        self.assertEqual(t.cor_hex, '#C8102E')
        self.assertEqual(Atleta.objects.count(), 1)
        self.assertEqual(Atleta.objects.get().overall, 85)

    def test_mesmo_time_de_duas_fontes_nao_duplica(self):
        importar.salvar_time({'nome': 'Flamengo', 'id': 1783, 'escudo': 'https://x/f.png'}, 'football-data')
        _, criado = importar.salvar_time({'nome': 'flamengo', 'id': 'abc', 'estadio': 'Maracanã'}, 'thesportsdb')
        self.assertFalse(criado)
        t = Time.objects.get()
        self.assertEqual(t.ids_externos, {'football-data': 1783, 'thesportsdb': 'abc'})
        self.assertEqual((t.escudo_url, t.estadio), ('https://x/f.png', 'Maracanã'))


class ProvedoresTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(FOOTBALL_DATA_TOKEN='x')
    def test_football_data_times_e_elenco(self):
        resp = {'competition': {'name': 'Campeonato Brasileiro Série A'}, 'teams': [{
            'id': 1783, 'name': 'CR Flamengo', 'shortName': 'Flamengo', 'tla': 'FLA', 'crest': 'https://c/f.png', 'founded': 1895,
            'venue': 'Maracanã', 'area': {'name': 'Brazil'},
            'squad': [{'id': 1, 'name': 'Rossi', 'position': 'Goalkeeper', 'dateOfBirth': '1995-12-04', 'nationality': 'Argentina'},
                      {'id': 2, 'name': 'Arrascaeta', 'position': 'Attacking Midfield', 'dateOfBirth': '1994-06-01', 'nationality': 'Uruguay'}]}]}
        with mock.patch('futebol.provedores.football_data.http_get_json', return_value=resp):
            r = importar.importar_provedor('football-data')
        self.assertEqual((r['times'], r['atletas']), (1, 2))
        self.assertEqual(Atleta.objects.get(nome='Arrascaeta').posicao, 'MEI')
        self.assertEqual(Time.objects.get().nome, 'Flamengo')

    def test_sem_token_football_data_vira_aviso_nao_excecao(self):
        with override_settings(FOOTBALL_DATA_TOKEN=None):
            r = importar.importar_provedor('football-data')
        self.assertTrue(r['erros'])
        self.assertEqual(r['times'], 0)

    def test_thesportsdb_busca_e_elenco(self):
        times = {'teams': [{'idTeam': '133', 'strTeam': 'Flamengo', 'strCountry': 'Brazil', 'strStadium': 'Maracanã', 'intFormedYear': '1895',
                            'strTeamBadge': 'https://b/f.png', 'strLeague': 'Brazilian Serie A'}]}
        elenco = {'player': [{'idPlayer': '9', 'strPlayer': 'Pedro', 'strPosition': 'Forward', 'strNumber': '9', 'dateBorn': '1997-06-20'}]}
        with mock.patch('futebol.provedores.thesportsdb.http_get_json', side_effect=[times, elenco]):
            r = importar.importar_provedor('thesportsdb', busca='Flamengo')
        self.assertEqual((r['times'], r['atletas']), (1, 1))
        self.assertEqual(Atleta.objects.get().posicao, 'ATA')

    def test_busca_obrigatoria_para_fontes_por_nome(self):
        r = importar.importar_provedor('thesportsdb')
        self.assertTrue(any('--buscar' in e for e in r['erros']))

    def test_espn_noticias_filtra_links_estranhos(self):
        resp = {'articles': [
            {'headline': 'Gol do Mengão', 'description': 'x', 'links': {'web': {'href': 'https://espn.com.br/a'}}, 'images': [{'url': 'https://i/1.jpg'}]},
            {'headline': 'Perigoso', 'links': {'web': {'href': 'javascript:alert(1)'}}},
            {'headline': '', 'links': {'web': {'href': 'https://espn.com.br/b'}}}]}
        with mock.patch('futebol.provedores.espn.http_get_json', return_value=resp):
            noticias = espn.noticias()
        self.assertEqual([n['titulo'] for n in noticias], ['Gol do Mengão'])
        self.assertEqual(noticias[0]['imagem'], 'https://i/1.jpg')

    def test_espn_placar(self):
        resp = {'events': [{'id': '1', 'date': '2026-10-03T22:00Z', 'status': {'type': {'state': 'in', 'shortDetail': "65'"}},
                            'competitions': [{'competitors': [
                                {'homeAway': 'home', 'score': '2', 'team': {'displayName': 'Flamengo', 'logo': 'l1'}},
                                {'homeAway': 'away', 'score': '1', 'team': {'displayName': 'Palmeiras', 'logo': 'l2'}}]}]}]}
        with mock.patch('futebol.provedores.espn.http_get_json', return_value=resp):
            jogos = espn.placar()
        self.assertEqual((jogos[0]['casa'], jogos[0]['gols_casa'], jogos[0]['estado']), ('Flamengo', '2', 'in'))

    def test_espn_elenco_plano_e_agrupado(self):
        a = {'id': '1', 'fullName': 'Rossi', 'position': {'abbreviation': 'G', 'displayName': 'Goalkeeper'}, 'jersey': '1'}
        b = {'id': '2', 'fullName': 'Pedro', 'position': {'abbreviation': 'F', 'displayName': 'Forward'}, 'jersey': '9'}
        for resp in ({'athletes': [a, b]}, {'athletes': [{'position': 'x', 'items': [a, b]}]}):
            with mock.patch('futebol.provedores.espn.http_get_json', return_value=resp):
                self.assertEqual([x['posicao'] for x in espn.elenco('1')], ['GOL', 'ATA'])

    def test_api_football_erro_de_cota_vira_indisponivel(self):
        with override_settings(APIFOOTBALL_KEY='k'), mock.patch('futebol.provedores.api_football.http_get_json',
                                                                 return_value={'errors': {'requests': 'limit'}, 'response': []}):
            with self.assertRaises(ProvedorIndisponivel):
                api_football.buscar_times('Fla')

    @override_settings(APIFOOTBALL_KEY='k')
    def test_api_football_previsao(self):
        fixtures = [{'fixture': {'id': 99}, 'teams': {'home': {'name': 'Flamengo'}, 'away': {'name': 'Palmeiras'}}}]
        pred = [{'predictions': {'advice': 'Double chance : Flamengo or draw', 'percent': {'home': '45%', 'draw': '30%', 'away': '25%'}}}]
        with mock.patch('futebol.provedores.api_football.http_get_json', side_effect=[{'errors': [], 'response': fixtures}, {'errors': [], 'response': pred}]):
            p = api_football.previsao_do_jogo('Flamengo', 'Palmeiras', '2026-10-03', 2026)
        self.assertEqual((p['casa'], p['empate'], p['fora']), (45, 30, 25))


class BuscaERaioXTests(TestCase):
    def setUp(self):
        cache.clear()
        self.fla = Time.objects.create(nome='Flamengo', pais='Brasil', liga='Brasileirão')
        Atleta.objects.create(nome='Gabriel Barbosa', time=self.fla, posicao='ATA')
        Atleta.objects.create(nome='Éverton Ribeiro', time=self.fla, posicao='MEI')

    def test_busca_ignora_acento_e_caixa(self):
        r = servico.buscar('everton')
        self.assertEqual([a.nome for a in r['jogadores']], ['Éverton Ribeiro'])
        self.assertEqual([t.nome for t in servico.buscar('FLAMENGO')['times']], ['Flamengo'])
        self.assertEqual(servico.buscar('a'), {'times': [], 'jogadores': []})

    def test_raio_x_com_dados_locais_funciona_sem_nenhuma_api(self):
        agora = timezone.now()
        for i, (gc, gf) in enumerate([(2, 0), (1, 1), (0, 3)]):
            Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=agora - timedelta(days=30 * (i + 1)),
                                gols_casa_real=gc, gols_fora_real=gf, finalizado=True, premio_distribuido=True)
        futuro = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=agora + timedelta(days=2))
        with override_settings(FOOTBALL_DATA_TOKEN=None, APIFOOTBALL_KEY=None):
            rx = servico.raio_x(futuro)
        self.assertEqual([f['resultado'] for f in rx['forma_casa']], ['D', 'E', 'V'])
        self.assertEqual(rx['resumo_h2h'], {'casa': 1, 'empates': 1, 'fora': 1})
        self.assertIsNone(rx['previsao'])
        self.assertEqual(rx['fontes'], ['banco do site'])

    def test_raio_x_usa_football_data_e_api_football_quando_disponiveis(self):
        self.fla.ids_externos = {'football-data': 1783}
        self.fla.save()
        jogo = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=timezone.now() + timedelta(days=1), external_id=555)
        ultimos = [{'data': '2026-09-01', 'casa': 'Flamengo', 'fora': 'X', 'placar': '1 x 0', 'resultado': 'V'}]
        h2h = [{'data': '2026-05-01', 'casa': 'Flamengo', 'fora': 'Palmeiras', 'placar': '2 x 1', 'gols_casa': 2, 'gols_fora': 1}]
        prev = {'casa': 50, 'empate': 30, 'fora': 20, 'conselho': 'x'}
        with override_settings(FOOTBALL_DATA_TOKEN='t', APIFOOTBALL_KEY='k'), \
                mock.patch.object(football_data, 'ultimos_jogos', return_value=ultimos), \
                mock.patch.object(football_data, 'confronto_direto', return_value=h2h), \
                mock.patch.object(servico, 'football_data_tabela', return_value=[
                    {'time': 'Flamengo', 'posicao': 1, 'pontos': 50}, {'time': 'Palmeiras', 'posicao': 2, 'pontos': 49}]), \
                mock.patch.object(api_football, 'previsao_do_jogo', return_value=prev), \
                mock.patch.object(api_football, 'lesoes', return_value={'Flamengo': [{'jogador': 'Pedro', 'motivo': 'Lesão'}]}):
            rx = servico.raio_x(jogo)
        self.assertEqual(rx['forma_casa'], ultimos)
        self.assertEqual(rx['h2h'], h2h)
        self.assertEqual(rx['previsao'], prev)
        self.assertEqual(rx['tabela']['casa']['posicao'], 1)
        self.assertEqual(rx['lesoes_casa'][0]['jogador'], 'Pedro')
        self.assertEqual(rx['fontes'], ['api-football', 'banco do site', 'football-data'])

    def test_raio_x_tolera_falha_dos_provedores(self):
        jogo = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=timezone.now() + timedelta(days=1), external_id=1)
        self.fla.ids_externos = {'football-data': 1}
        self.fla.save()
        with override_settings(FOOTBALL_DATA_TOKEN='t', APIFOOTBALL_KEY='k'), \
                mock.patch.object(football_data, 'ultimos_jogos', side_effect=ProvedorIndisponivel('x')), \
                mock.patch.object(football_data, 'confronto_direto', side_effect=ProvedorIndisponivel('x')), \
                mock.patch.object(servico, 'football_data_tabela', side_effect=ProvedorIndisponivel('x')), \
                mock.patch.object(api_football, 'previsao_do_jogo', side_effect=ProvedorIndisponivel('x')):
            rx = servico.raio_x(jogo)
        self.assertEqual(rx['fontes'], ['banco do site'])


class ComparativoTests(TestCase):
    def setUp(self):
        self.a = Time.objects.create(nome='Flamengo', pais='Brasil')
        self.b = Time.objects.create(nome='Palmeiras', pais='Brasil')
        cria_elenco(self.a, 'Fla')
        cria_elenco(self.b, 'Pal')
        self.criador = User.objects.create_user('criador', password='x', first_name='Criador')
        self.ids_a = [x.id for x in regras.sugerir_titulares(self.a)]
        self.ids_b = [x.id for x in regras.sugerir_titulares(self.b)]

    def test_sugestao_e_433_com_os_melhores(self):
        titulares = regras.sugerir_titulares(self.a)
        self.assertEqual(len(titulares), 11)
        from collections import Counter
        self.assertEqual(Counter(x.posicao for x in titulares), {'GOL': 1, 'DEF': 4, 'MEI': 3, 'ATA': 3})

    def test_criar_valida_11_goleiro_e_time_certo(self):
        comp = regras.criar(self.criador, self.a, self.b, self.ids_a, self.ids_b, 'Quem tem o melhor?')
        self.assertEqual(comp.iniciais.count(), 22)
        with self.assertRaises(regras.ComparativoInvalido):
            regras.criar(self.criador, self.a, self.b, self.ids_a[:10], self.ids_b)
        with self.assertRaises(regras.ComparativoInvalido):
            regras.criar(self.criador, self.a, self.b, self.ids_b, self.ids_a)             # lados trocados
        with self.assertRaises(regras.ComparativoInvalido):
            regras.criar(self.criador, self.a, self.a, self.ids_a, self.ids_a)
        sem_goleiro = [x.id for x in self.a.atletas.exclude(posicao='GOL')[:11]]
        with self.assertRaises(regras.ComparativoInvalido):
            regras.criar(self.criador, self.a, self.b, sem_goleiro, self.ids_b)

    def _comp(self):
        return regras.criar(self.criador, self.a, self.b, self.ids_a, self.ids_b)

    def _voto_valido(self, comp, preferir='A'):
        escolhidos = []
        for pos, qtd in regras.FORMACAO.items():
            cands = [e for e in regras.candidatos(comp) if e.atleta.posicao == pos]
            cands.sort(key=lambda e: (e.lado != preferir, e.atleta.nome))
            escolhidos += [e.atleta_id for e in cands[:qtd]]
        return escolhidos

    def test_voto_exige_433_exato_e_paga_so_o_primeiro(self):
        comp = self._comp()
        u = User.objects.create_user('votante', password='x')
        with self.assertRaises(regras.ComparativoInvalido):
            regras.votar(u, comp, self._voto_valido(comp)[:10])
        votos = self._voto_valido(comp)
        self.assertTrue(regras.votar(u, comp, votos))
        self.assertEqual(coins.saldo(u), 1000 + regras.RECOMPENSA_VOTO)
        self.assertFalse(regras.votar(u, comp, self._voto_valido(comp, 'B')))      # troca de voto
        self.assertEqual(coins.saldo(u), 1000 + regras.RECOMPENSA_VOTO)
        self.assertEqual(Voto.objects.filter(usuario=u).count(), 11)

    def test_nao_vota_em_quem_nao_esta_entre_os_22_nem_apos_encerrar(self):
        comp = self._comp()
        u = User.objects.create_user('votante', password='x')
        fora = self.a.atletas.exclude(pk__in=self.ids_a).first()
        with self.assertRaises(regras.ComparativoInvalido):
            regras.votar(u, comp, self._voto_valido(comp)[:10] + [fora.id])
        comp.encerrado = True
        comp.save()
        with self.assertRaises(regras.ComparativoInvalido):
            regras.votar(u, comp, self._voto_valido(comp))

    def test_apuracao_elege_os_mais_votados_e_conta_por_time(self):
        comp = self._comp()
        for i in range(3):
            regras.votar(User.objects.create_user(f'a{i}', password='x'), comp, self._voto_valido(comp, 'A'))
        regras.votar(User.objects.create_user('b0', password='x'), comp, self._voto_valido(comp, 'B'))
        ap = regras.apuracao(comp)
        self.assertEqual(ap['votantes'], 4)
        self.assertEqual(ap['placar'], {'A': 11, 'B': 0})
        self.assertEqual(ap['vencedor'], 'A')
        self.assertEqual([len(l['jogadores']) for l in ap['linhas']], [3, 3, 4, 1])
        self.assertEqual(ap['linhas'][0]['jogadores'][0]['pct'], 75)

    def test_sem_votos_nao_quebra(self):
        ap = regras.apuracao(self._comp())
        self.assertEqual((ap['votantes'], ap['vencedor']), (0, None))


class ViewsFutebolTests(TestCase):
    def setUp(self):
        cache.clear()
        self.u = User.objects.create_user('craque', password='x', first_name='Craque')
        self.client.force_login(self.u)
        self.a = Time.objects.create(nome='Flamengo', pais='Brasil', cor='#C8102E')
        self.b = Time.objects.create(nome='Palmeiras', pais='Brasil', cor='#006437')
        cria_elenco(self.a, 'Fla')
        cria_elenco(self.b, 'Pal')

    def test_paginas_basicas(self):
        atleta = Atleta.objects.first()
        for nome, args in (('hub', []), ('buscar', []), ('time', [self.a.id]), ('jogador', [atleta.id]), ('tabela', []),
                           ('artilharia', []), ('comparar', []), ('comparativo_lista', [])):
            self.assertEqual(self.client.get(reverse(f'futebol:{nome}', args=args)).status_code, 200, nome)

    def test_api_buscar_json(self):
        d = self.client.get(reverse('futebol:api_buscar') + '?q=flame').json()
        self.assertEqual(d['times'][0]['nome'], 'Flamengo')
        d = self.client.get(reverse('futebol:api_buscar') + '?q=fla gol').json()
        self.assertEqual(d['times'], [])

    def test_comparar_mostra_numeros(self):
        r = self.client.get(reverse('futebol:comparar') + f'?a={self.a.id}&b={self.b.id}')
        self.assertContains(r, 'Escolher os 11 iniciais')
        self.assertContains(r, 'Overall médio')

    def test_fluxo_completo_criar_votar_encerrar(self):
        ids_a = [x.id for x in regras.sugerir_titulares(self.a)]
        ids_b = [x.id for x in regras.sugerir_titulares(self.b)]
        r = self.client.get(reverse('futebol:comparativo_novo') + f'?a={self.a.id}&b={self.b.id}')
        self.assertContains(r, 'Escolha os 11 iniciais')
        r = self.client.post(reverse('futebol:comparativo_novo'), {'a': self.a.id, 'b': self.b.id, 'lado_a': ids_a, 'lado_b': ids_b, 'titulo': 'Teste'})
        comp = Comparativo.objects.get()
        self.assertRedirects(r, reverse('futebol:comparativo', args=[comp.pk]))

        escolhidos = []
        for pos, qtd in regras.FORMACAO.items():
            escolhidos += [e.atleta_id for e in regras.candidatos(comp) if e.atleta.posicao == pos][:qtd]
        r = self.client.post(reverse('futebol:comparativo_votar', args=[comp.pk]), {'atleta': escolhidos})
        self.assertEqual(r.status_code, 302)
        page = self.client.get(reverse('futebol:comparativo', args=[comp.pk]))
        self.assertContains(page, 'O 11 eleito')
        self.assertContains(page, 'Veredito da galera')

        outro = User.objects.create_user('outro', password='x')
        self.client.force_login(outro)
        self.assertEqual(self.client.post(reverse('futebol:comparativo_encerrar', args=[comp.pk])).status_code, 404)
        self.client.force_login(self.u)
        self.client.post(reverse('futebol:comparativo_encerrar', args=[comp.pk]))
        comp.refresh_from_db()
        self.assertTrue(comp.encerrado)

    def test_criar_sem_times_volta_para_comparar(self):
        r = self.client.get(reverse('futebol:comparativo_novo'))
        self.assertRedirects(r, reverse('futebol:comparar'))

    def test_anonimo_nao_acessa(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('futebol:hub')).status_code, 302)

    def test_raio_x_json(self):
        jogo = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=timezone.now() + timedelta(days=1))
        with override_settings(FOOTBALL_DATA_TOKEN=None, APIFOOTBALL_KEY=None):
            d = self.client.get(reverse('futebol:api_raio_x', args=[jogo.id])).json()
        self.assertEqual(d['casa'], 'Flamengo')


class EscudosGlobaisTests(TestCase):
    def test_chave_ignora_ruido_e_acentos(self):
        from futebol.escudos import chave_time
        self.assertEqual(chave_time('C.R. Flamengo'), chave_time('Flamengo'))
        self.assertEqual(chave_time('São Paulo FC'), 'sao paulo')
        self.assertNotEqual(chave_time('Atlético-MG'), chave_time('Atlético-GO'))

    def test_jogo_usa_escudo_global(self):
        from datetime import timedelta
        from django.utils import timezone
        from futebol.escudos import registrar
        from palpites.models import Jogo
        registrar('Flamengo', url='https://x.test/fla.png')
        j = Jogo.objects.create(time_casa='CR Flamengo', time_fora='Vasco', data_hora=timezone.now() + timedelta(days=1))
        self.assertEqual(j.escudo_casa_src, 'https://x.test/fla.png')
        self.assertIsNone(j.escudo_fora_src)

    def test_comando_aplicar_registra_urls_de_jogos(self):
        from datetime import timedelta
        from django.core.management import call_command
        from django.utils import timezone
        from futebol.models import Escudo
        from palpites.models import Jogo
        Jogo.objects.create(time_casa='Santos', time_fora='Bahia', data_hora=timezone.now() + timedelta(days=1),
                            escudo_casa_url='https://x.test/santos.png')
        call_command('consolidar_escudos', '--aplicar', stdout=__import__('io').StringIO())
        self.assertTrue(Escudo.objects.filter(chave='santos', url='https://x.test/santos.png').exists())

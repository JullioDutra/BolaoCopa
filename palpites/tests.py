import json
from datetime import timedelta
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts import coins
from accounts.models import Carteira
from . import api_futebol, sincronizacao
from .models import InscricaoRodada, Jogo, Palpite, RodadaBolao


def criar_usuario(nome, saldo='100.00'):
    u = User.objects.create_user(nome, password='x', first_name=nome)
    Carteira.objects.update_or_create(usuario=u, defaults={'saldo': Decimal(saldo)})
    return u


class NomeCanonicoTests(TestCase):
    def test_nomes_da_api_viram_nomes_do_banco(self):
        casos = [
            ({'shortName': 'Flamengo', 'name': 'CR Flamengo'}, 'Flamengo'),
            ({'shortName': 'Atlético Mineiro', 'name': 'CA Mineiro'}, 'Atlético-MG'),
            ({'shortName': 'Athletico-PR', 'name': 'CA Paranaense'}, 'Athletico-PR'),
            ({'shortName': 'Vasco da Gama', 'name': 'CR Vasco da Gama'}, 'Vasco'),
            ({'shortName': 'Grêmio', 'name': 'Grêmio FBPA'}, 'Grêmio'),
            ({'shortName': 'São Paulo', 'name': 'São Paulo FC'}, 'São Paulo'),
            ({'shortName': 'Bragantino', 'name': 'RB Bragantino'}, 'Bragantino'),
        ]
        for time_api, esperado in casos:
            self.assertEqual(api_futebol.nome_canonico(time_api), esperado)


def partida_api(id_, rodada=10, status='TIMED', casa='Flamengo', fora='Palmeiras', placar=(None, None), quando=None):
    quando = quando or (timezone.now() + timedelta(days=2))
    return {
        'external_id': id_, 'data_hora': quando.strftime('%Y-%m-%dT%H:%M:%SZ'), 'status': status,
        'rodada': rodada, 'casa': casa, 'fora': fora,
        'escudo_casa': 'https://crests.football-data.org/1783.png', 'escudo_fora': '',
        'gols_casa': placar[0], 'gols_fora': placar[1],
    }


class SincronizacaoTests(TestCase):
    def test_cria_jogos_e_rodada_sem_duplicar(self):
        lote = [partida_api(1), partida_api(2, casa='Santos', fora='Vasco')]
        with mock.patch.object(api_futebol, 'partidas', return_value=lote):
            r1 = sincronizacao.sincronizar(rodada=10)
            r2 = sincronizacao.sincronizar(rodada=10)
        self.assertEqual((r1['criados'], r2['criados'], r2['atualizados']), (2, 0, 2))
        self.assertEqual(Jogo.objects.count(), 2)
        self.assertEqual(RodadaBolao.objects.count(), 1)
        jogo = Jogo.objects.get(external_id=1)
        self.assertEqual(jogo.rodada.numero, 10)
        self.assertTrue(jogo.escudo_casa_src.startswith('https://'))

    def test_finalizar_paga_pontos_e_coins_uma_vez(self):
        usuario = criar_usuario('ana')
        with mock.patch.object(api_futebol, 'partidas', return_value=[partida_api(1)]):
            sincronizacao.sincronizar(rodada=10)
        jogo = Jogo.objects.get(external_id=1)
        Palpite.objects.create(usuario=usuario, jogo=jogo, gols_casa=2, gols_fora=1)

        final = partida_api(1, status='FINISHED', placar=(2, 1))
        with mock.patch.object(api_futebol, 'partidas', return_value=[final]):
            resumo = sincronizacao.sincronizar(rodada=10)
            sincronizacao.sincronizar(rodada=10)  # segunda rodada de sync não pode pagar de novo
        self.assertEqual(resumo['finalizados'], 1)
        palpite = Palpite.objects.get()
        self.assertEqual(palpite.pontuacao_obtida, 15)
        # +50 pelo placar exato (uma única vez) e +25 x2 pelas conquistas "Estreante" e "Cravador"
        self.assertEqual(coins.saldo(usuario), 1000 + 50 + 25 + 25)
        self.assertEqual(usuario.carteira_coins.movimentos.filter(valor=50).count(), 1)

    def test_placar_ao_vivo_nao_finaliza(self):
        parcial = partida_api(1, status='IN_PLAY', placar=(1, 0))
        with mock.patch.object(api_futebol, 'partidas', return_value=[parcial]):
            sincronizacao.sincronizar(rodada=10)
        jogo = Jogo.objects.get()
        self.assertFalse(jogo.finalizado)
        self.assertTrue(jogo.ao_vivo)
        self.assertEqual(jogo.gols_casa_real, 1)

    def test_jogo_finalizado_manualmente_nao_e_sobrescrito(self):
        with mock.patch.object(api_futebol, 'partidas', return_value=[partida_api(1)]):
            sincronizacao.sincronizar(rodada=10)
        jogo = Jogo.objects.get()
        jogo.gols_casa_real, jogo.gols_fora_real, jogo.finalizado = 3, 3, True
        jogo.save()
        final = partida_api(1, status='FINISHED', placar=(0, 0))
        with mock.patch.object(api_futebol, 'partidas', return_value=[final]):
            sincronizacao.sincronizar(rodada=10)
        jogo.refresh_from_db()
        self.assertEqual((jogo.gols_casa_real, jogo.gols_fora_real), (3, 3))

    def test_sem_token_levanta_api_indisponivel(self):
        with override_settings(FOOTBALL_DATA_TOKEN=None):
            with self.assertRaises(api_futebol.ApiIndisponivel):
                api_futebol.partidas()


class BolaoDaRodadaTests(TestCase):
    def setUp(self):
        self.rodada = RodadaBolao.objects.create(nome='Brasileirão — Rodada 1', numero=1)
        futuro = timezone.now() + timedelta(days=2)
        self.j1 = Jogo.objects.create(time_casa='A', time_fora='B', data_hora=futuro, rodada=self.rodada)
        self.j2 = Jogo.objects.create(time_casa='C', time_fora='D', data_hora=futuro + timedelta(hours=3), rodada=self.rodada)
        self.ana = criar_usuario('ana')
        self.bia = criar_usuario('bia')
        self.cris = criar_usuario('cris')

    def entrar(self, usuario):
        self.client.force_login(usuario)
        return self.client.post(reverse('palpites:entrar_rodada', args=[self.rodada.id]))

    def test_entrar_cobra_uma_vez(self):
        self.entrar(self.ana)
        self.entrar(self.ana)
        self.ana.carteira.refresh_from_db()
        self.assertEqual(self.ana.carteira.saldo, Decimal('90.00'))
        self.assertEqual(InscricaoRodada.objects.filter(usuario=self.ana).count(), 1)

    def test_saldo_insuficiente_nao_inscreve(self):
        pobre = criar_usuario('pobre', saldo='5.00')
        self.entrar(pobre)
        self.assertFalse(InscricaoRodada.objects.filter(usuario=pobre).exists())

    def test_inscricao_fechada_na_ultima_hora(self):
        self.j1.data_hora = timezone.now() + timedelta(minutes=30)
        self.j1.save()
        self.entrar(self.ana)
        self.assertFalse(InscricaoRodada.objects.exists())

    def test_inscricao_converte_palpites_resenha_existentes(self):
        Palpite.objects.create(usuario=self.ana, jogo=self.j1, gols_casa=1, gols_fora=0)
        self.entrar(self.ana)
        self.assertEqual(Palpite.objects.get().modalidade, 'rodada')

    def test_palpite_na_modalidade_rodada_exige_inscricao(self):
        self.client.force_login(self.ana)
        r = self.client.post(reverse('palpites:fazer_palpite', args=[self.j1.id]),
                             {'gols_casa': 1, 'gols_fora': 0, 'tipo_aposta': 'rodada'})
        self.assertEqual(r.status_code, 302)
        self.assertFalse(Palpite.objects.exists())

        self.entrar(self.ana)
        self.client.post(reverse('palpites:fazer_palpite', args=[self.j1.id]),
                         {'gols_casa': 1, 'gols_fora': 0, 'tipo_aposta': 'rodada'})
        self.assertEqual(Palpite.objects.get().modalidade, 'rodada')

    def _finalizar(self, jogo, casa, fora):
        jogo.gols_casa_real, jogo.gols_fora_real, jogo.finalizado = casa, fora, True
        jogo.save()

    def test_lider_da_rodada_leva_o_pote_apos_o_ultimo_jogo(self):
        for u in (self.ana, self.bia, self.cris):
            self.entrar(u)
        # ana crava os dois (30), bia crava um e acerta o vencedor do outro (20), cris só o vencedor (10)
        Palpite.objects.create(usuario=self.ana, jogo=self.j1, gols_casa=2, gols_fora=0, modalidade='rodada')
        Palpite.objects.create(usuario=self.ana, jogo=self.j2, gols_casa=1, gols_fora=1, modalidade='rodada')
        Palpite.objects.create(usuario=self.bia, jogo=self.j1, gols_casa=2, gols_fora=0, modalidade='rodada')
        Palpite.objects.create(usuario=self.bia, jogo=self.j2, gols_casa=2, gols_fora=2, modalidade='rodada')
        Palpite.objects.create(usuario=self.cris, jogo=self.j1, gols_casa=1, gols_fora=0, modalidade='rodada')

        self._finalizar(self.j1, 2, 0)
        self.rodada.refresh_from_db()
        self.assertFalse(self.rodada.premio_distribuido)  # ainda falta um jogo

        self._finalizar(self.j2, 1, 1)
        self.rodada.refresh_from_db()
        self.assertTrue(self.rodada.premio_distribuido)

        self.ana.carteira.refresh_from_db()
        # entrou com 100, pagou 10, pote = 30 - 5% = 28,50
        self.assertEqual(self.ana.carteira.saldo, Decimal('90.00') + Decimal('28.50'))
        self.bia.carteira.refresh_from_db()
        self.assertEqual(self.bia.carteira.saldo, Decimal('90.00'))

        # salvar de novo não paga duas vezes
        self._finalizar(self.j2, 1, 1)
        self.ana.carteira.refresh_from_db()
        self.assertEqual(self.ana.carteira.saldo, Decimal('118.50'))

    def test_empate_no_topo_divide_o_pote(self):
        for u in (self.ana, self.bia):
            self.entrar(u)
        for u in (self.ana, self.bia):
            Palpite.objects.create(usuario=u, jogo=self.j1, gols_casa=1, gols_fora=0, modalidade='rodada')
            Palpite.objects.create(usuario=u, jogo=self.j2, gols_casa=1, gols_fora=0, modalidade='rodada')
        self._finalizar(self.j1, 1, 0)
        self._finalizar(self.j2, 1, 0)
        self.ana.carteira.refresh_from_db()
        self.bia.carteira.refresh_from_db()
        # pote 20 - 5% = 19 -> 9,50 cada
        self.assertEqual(self.ana.carteira.saldo, Decimal('99.50'))
        self.assertEqual(self.bia.carteira.saldo, Decimal('99.50'))

    def test_telas_renderizam(self):
        self.client.force_login(self.ana)
        self.assertContains(self.client.get(reverse('palpites:listar_jogos')), 'Uma entrada, a rodada inteira')
        self.assertEqual(self.client.get(reverse('palpites:ranking_rodada', args=[self.rodada.id])).status_code, 200)
        self.assertEqual(self.client.get(reverse('palpites:fazer_palpite', args=[self.j1.id])).status_code, 200)


class EndpointCronTests(TestCase):
    def test_desligado_sem_token_configurado(self):
        with override_settings(SYNC_SECRET_TOKEN=None):
            self.assertEqual(self.client.get('/palpites/api/sincronizar/qualquer/').status_code, 404)

    @override_settings(SYNC_SECRET_TOKEN='segredo-de-teste')
    def test_token_errado_404_e_certo_executa(self):
        self.assertEqual(self.client.get('/palpites/api/sincronizar/errado/').status_code, 404)
        with mock.patch.object(api_futebol, 'rodada_atual', return_value=10), \
                mock.patch.object(api_futebol, 'partidas', return_value=[partida_api(7)]):
            r = self.client.get('/palpites/api/sincronizar/segredo-de-teste/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.content)['criados'], 1)

    @override_settings(SYNC_SECRET_TOKEN='segredo-de-teste', FOOTBALL_DATA_TOKEN=None)
    def test_api_fora_do_ar_responde_503(self):
        self.assertEqual(self.client.get('/palpites/api/sincronizar/segredo-de-teste/').status_code, 503)



class ArenaTests(TestCase):
    def setUp(self):
        self.u = criar_usuario('ana')
        self.client.force_login(self.u)
        futuro = timezone.now() + timedelta(days=2)
        self.jogo = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=futuro)

    def test_palpite_rapido_cria_atualiza_e_mantem_modalidade_paga(self):
        url = reverse('palpites:palpite_rapido', args=[self.jogo.id])
        r = self.client.post(url, {'gols_casa': 2, 'gols_fora': 1})
        self.assertEqual((r.status_code, r.json()['novo']), (200, True))
        p = Palpite.objects.get()
        self.assertEqual((p.gols_casa, p.gols_fora, p.modalidade), (2, 1, 'resenha'))
        p.modalidade = 'pago'
        p.save()
        r = self.client.post(url, {'gols_casa': 3, 'gols_fora': 3})
        self.assertFalse(r.json()['novo'])
        p.refresh_from_db()
        self.assertEqual((p.gols_casa, p.modalidade), (3, 'pago'))

    def test_palpite_rapido_valida_placar_e_prazo(self):
        url = reverse('palpites:palpite_rapido', args=[self.jogo.id])
        for dados in ({'gols_casa': 'x', 'gols_fora': 1}, {'gols_casa': 21, 'gols_fora': 1}, {'gols_casa': -1, 'gols_fora': 0}, {}):
            self.assertEqual(self.client.post(url, dados).status_code, 400)
        self.jogo.data_hora = timezone.now() + timedelta(minutes=30)
        self.jogo.save()
        self.assertEqual(self.client.post(url, {'gols_casa': 1, 'gols_fora': 0}).status_code, 400)
        self.assertFalse(Palpite.objects.exists())
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_arena_mostra_estados_progresso_e_galera_so_depois_de_palpitar(self):
        outro = criar_usuario('bia')
        Palpite.objects.create(usuario=outro, jogo=self.jogo, gols_casa=1, gols_fora=0)
        r = self.client.get(reverse('palpites:listar_jogos'))
        self.assertContains(r, '0 de 1 jogos abertos palpitados')
        self.assertNotContains(r, 'palpite da galera')                      # não revela a tendência antes de palpitar
        self.client.post(reverse('palpites:palpite_rapido', args=[self.jogo.id]), {'gols_casa': 2, 'gols_fora': 0})
        r = self.client.get(reverse('palpites:listar_jogos'))
        self.assertContains(r, '1 de 1 jogos abertos palpitados')
        self.assertContains(r, '2 palpites da galera')

    def test_arena_resultado_cravou_acertou_errou(self):
        passado = timezone.now() - timedelta(days=1)
        for gc, gf, esperado in ((2, 0, 'Cravou'), (1, 0, 'Acertou o vencedor'), (0, 2, 'Dessa vez')):
            j = Jogo.objects.create(time_casa='A%s' % gc, time_fora='B', data_hora=passado)
            Palpite.objects.create(usuario=self.u, jogo=j, gols_casa=gc, gols_fora=gf)
            j.gols_casa_real, j.gols_fora_real, j.finalizado = 2, 0, True
            j.save()
        r = self.client.get(reverse('palpites:listar_jogos'))
        for texto in ('Cravou', 'Acertou o vencedor', 'Dessa vez'):
            self.assertContains(r, texto)

    def test_tela_de_palpite_traz_raio_x_e_zap(self):
        Palpite.objects.create(usuario=self.u, jogo=self.jogo, gols_casa=1, gols_fora=1)
        r = self.client.get(reverse('palpites:fazer_palpite', args=[self.jogo.id]))
        self.assertContains(r, 'Raio')
        self.assertContains(r, 'wa.me')
        self.assertContains(r, reverse('futebol:api_raio_x', args=[self.jogo.id]))

    def test_cravada_gera_feed_conquista_e_aviso(self):
        from avisos.models import Atividade, Conquista
        passado = timezone.now() - timedelta(days=1)
        j = Jogo.objects.create(time_casa='A', time_fora='B', data_hora=passado)
        Palpite.objects.create(usuario=self.u, jogo=j, gols_casa=2, gols_fora=0)
        j.gols_casa_real, j.gols_fora_real, j.finalizado = 2, 0, True
        j.save()
        self.assertTrue(Atividade.objects.filter(tipo='cravada').exists())
        slugs = set(Conquista.objects.filter(usuario=self.u).values_list('slug', flat=True))
        self.assertTrue({'estreante', 'cravador'} <= slugs)

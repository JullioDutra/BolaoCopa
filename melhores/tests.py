from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts import coins
from accounts.models import CarteiraCoins

from . import services
from .dados_historicos import CATEGORIAS
from .models import Aposta, Candidato, Categoria, Edicao
from .odds import ODD_MAX, ODD_MIN, calcular_odds


class SeedEOddsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_melhores', '--ano', '2026', verbosity=0)
        cls.edicao = Edicao.objects.get(ano=2026)

    def test_seed_cria_todas_as_categorias_e_e_idempotente(self):
        total = Candidato.objects.count()
        self.assertEqual(self.edicao.categorias.count(), len(CATEGORIAS))
        call_command('seed_melhores', '--ano', '2026', verbosity=0)
        self.assertEqual(Candidato.objects.count(), total)

    def test_dados_historicos_somam_26_respostas_por_categoria_de_pessoa(self):
        # Cada categoria de pessoa/nome do formulário de 2025 teve 26 respostas.
        for slug, nome, _e, tipo, _d, cands in CATEGORIAS:
            if tipo in ('pessoa', 'nome'):
                self.assertEqual(sum(v25 for v25, _ in cands.values()), 26, slug)

    def test_favorito_paga_menos_que_azarao(self):
        cat = Categoria.objects.get(edicao=self.edicao, slug='cartoleiro')
        odds = calcular_odds(cat)
        adilson = cat.candidatos.get(nome='Adilson')
        filipe = cat.candidatos.get(nome='Filipe')
        self.assertLess(odds[adilson.id], Decimal('3'))
        self.assertGreater(odds[filipe.id], odds[adilson.id] * 5)

    def test_odds_respeitam_limites_e_margem(self):
        for cat in self.edicao.categorias.all():
            odds = calcular_odds(cat)
            self.assertTrue(all(ODD_MIN <= o <= ODD_MAX for o in odds.values()), cat.slug)
            # Soma das probabilidades implícitas fica perto de 1/(1-margem) (sem os clamps)
            implicita = sum(1 / o for o in odds.values())
            self.assertGreater(implicita, Decimal('1'), cat.slug)

    def test_apostas_da_galera_derrubam_a_odd(self):
        cat = Categoria.objects.get(edicao=self.edicao, slug='cartoleiro')
        mark = cat.candidatos.get(nome='Mark')
        antes = calcular_odds(cat)[mark.id]
        for i in range(10):
            u = User.objects.create_user(f'u{i}', password='x')
            services.apostar(u, cat.id, mark.id, 500)
        depois = calcular_odds(cat)[mark.id]
        self.assertLess(depois, antes)


class ApostaTests(TestCase):
    def setUp(self):
        call_command('seed_melhores', '--ano', '2026', verbosity=0)
        self.cat = Categoria.objects.get(slug='vagabundo')
        self.mark = self.cat.candidatos.get(nome='Mark')
        self.matheus = self.cat.candidatos.get(nome='Matheus Santiago')
        self.user = User.objects.create_user('craque', password='x')

    def test_carteira_nasce_com_1000_coins(self):
        self.assertEqual(coins.saldo(self.user), 1000)
        self.assertEqual(self.user.carteira_coins.movimentos.count(), 1)

    def test_apostar_debita_e_trava_odd(self):
        aposta = services.apostar(self.user, self.cat.id, self.mark.id, 200)
        self.assertEqual(coins.saldo(self.user), 800)
        self.assertGreaterEqual(aposta.odd_travada, ODD_MIN)
        self.assertEqual(aposta.status, 'aberta')

    def test_trocar_aposta_devolve_o_valor_antigo(self):
        services.apostar(self.user, self.cat.id, self.mark.id, 300)
        services.apostar(self.user, self.cat.id, self.matheus.id, 100)
        self.assertEqual(coins.saldo(self.user), 900)
        self.assertEqual(Aposta.objects.filter(usuario=self.user).count(), 1)
        self.assertEqual(Aposta.objects.get(usuario=self.user).candidato, self.matheus)

    def test_saldo_insuficiente_nao_altera_nada(self):
        with self.assertRaises(services.ApostaInvalida):
            services.apostar(self.user, self.cat.id, self.mark.id, 5000)
        self.assertEqual(coins.saldo(self.user), 1000)
        self.assertFalse(Aposta.objects.exists())

    def test_falha_ao_trocar_por_valor_maior_que_saldo_preserva_aposta_antiga(self):
        services.apostar(self.user, self.cat.id, self.mark.id, 300)
        with self.assertRaises(services.ApostaInvalida):
            services.apostar(self.user, self.cat.id, self.matheus.id, 5000)
        self.assertEqual(coins.saldo(self.user), 700)
        self.assertEqual(Aposta.objects.get(usuario=self.user).candidato, self.mark)

    def test_valor_minimo_e_valor_invalido(self):
        for ruim in (0, 9, -50, 'abc', None):
            with self.assertRaises(services.ApostaInvalida):
                services.apostar(self.user, self.cat.id, self.mark.id, ruim)

    def test_candidato_de_outra_categoria_e_rejeitado(self):
        outro = Candidato.objects.exclude(categoria=self.cat).first()
        with self.assertRaises(services.ApostaInvalida):
            services.apostar(self.user, self.cat.id, outro.id, 100)

    def test_categoria_fechada_nao_aceita_aposta(self):
        self.cat.aberta = False
        self.cat.save()
        with self.assertRaises(services.ApostaInvalida):
            services.apostar(self.user, self.cat.id, self.mark.id, 100)

    def test_liquidar_paga_vencedores_uma_unica_vez(self):
        aposta = services.apostar(self.user, self.cat.id, self.mark.id, 200)
        perdedor = User.objects.create_user('perdedor', password='x')
        services.apostar(perdedor, self.cat.id, self.matheus.id, 200)

        services.liquidar(self.cat.id, self.mark.id)
        aposta.refresh_from_db()
        self.assertEqual(aposta.status, 'ganha')
        esperado = 800 + int(Decimal(200) * aposta.odd_travada)
        self.assertEqual(coins.saldo(self.user), esperado)
        self.assertEqual(coins.saldo(perdedor), 800)
        self.assertEqual(Aposta.objects.get(usuario=perdedor).status, 'perdida')

        with self.assertRaises(services.ApostaInvalida):
            services.liquidar(self.cat.id, self.mark.id)
        self.assertEqual(coins.saldo(self.user), esperado)

    def test_anular_devolve_tudo(self):
        services.apostar(self.user, self.cat.id, self.mark.id, 250)
        services.anular(self.cat.id)
        self.assertEqual(coins.saldo(self.user), 1000)
        self.assertEqual(Aposta.objects.get(usuario=self.user).status, 'anulada')

    def test_ranking_conta_coins_em_jogo(self):
        services.apostar(self.user, self.cat.id, self.mark.id, 400)
        linhas = services.ranking(Edicao.objects.get(ano=2026))
        self.assertEqual(linhas[0]['patrimonio'], 1000)
        self.assertEqual(linhas[0]['em_jogo'], 400)


class ViewsTests(TestCase):
    def setUp(self):
        call_command('seed_melhores', '--ano', '2026', verbosity=0)
        self.user = User.objects.create_user('craque', password='x', first_name='Craque')
        self.client.force_login(self.user)
        self.cat = Categoria.objects.get(slug='mais-chato')
        self.mark = self.cat.candidatos.get(nome='Mark')

    def test_home_renderiza_com_odds(self):
        r = self.client.get(reverse('melhores:home'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Mais Chato do Ano')
        self.assertContains(r, '1000')

    def test_apostar_via_post(self):
        r = self.client.post(reverse('melhores:apostar', args=[self.cat.id]),
                             {'candidato': self.mark.id, 'valor': 150})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(coins.saldo(self.user), 850)
        self.assertTrue(r['Location'].endswith('#cat-mais-chato'))

    def test_api_odds_json(self):
        r = self.client.get(reverse('melhores:api_odds'))
        self.assertEqual(r.status_code, 200)
        self.assertIn(str(self.cat.id), r.json()['odds'])

    def test_staff_so_para_staff(self):
        self.assertEqual(self.client.get(reverse('melhores:staff')).status_code, 302)
        self.user.is_staff = True
        self.user.save()
        self.assertEqual(self.client.get(reverse('melhores:staff')).status_code, 200)

    def test_paginas_secundarias(self):
        for nome in ('melhores:minhas', 'melhores:ranking'):
            self.assertEqual(self.client.get(reverse(nome)).status_code, 200, nome)

    def test_anonimo_vai_para_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('melhores:home')).status_code, 302)

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from palpites.models import Clube

from . import coins, streak
from .models import PerfilUsuario
from .temas import luminosidade, tema_para_clube


class CoinsTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('a', password='x')

    def test_saldo_inicial_e_extrato(self):
        self.assertEqual(coins.saldo(self.u), 1000)
        coins.debitar(self.u, 300, 'teste')
        coins.creditar(self.u, 50, 'teste')
        self.assertEqual(coins.saldo(self.u), 750)
        self.assertEqual(self.u.carteira_coins.movimentos.count(), 3)

    def test_nao_deixa_saldo_negativo(self):
        with self.assertRaises(coins.SaldoInsuficiente):
            coins.debitar(self.u, 1001, 'x')
        self.assertEqual(coins.saldo(self.u), 1000)

    def test_valores_nao_positivos_sao_rejeitados(self):
        for fn in (coins.creditar, coins.debitar):
            with self.assertRaises(ValueError):
                fn(self.u, 0, 'x')
            with self.assertRaises(ValueError):
                fn(self.u, -5, 'x')


class StreakTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('a', password='x')
        self.d0 = date(2026, 10, 1)

    def test_bonus_escala_e_tem_premio_na_semana_perfeita(self):
        self.assertEqual([streak.bonus_do_dia(n) for n in range(1, 8)], [25, 40, 55, 70, 85, 100, 100 + 200])
        self.assertEqual(streak.bonus_do_dia(8), 100)

    def test_dias_seguidos_aumentam_e_falta_zera(self):
        r1 = streak.registrar_acesso(self.u, self.d0)
        r2 = streak.registrar_acesso(self.u, self.d0 + timedelta(days=1))
        self.assertEqual((r1['streak'], r2['streak']), (1, 2))
        r3 = streak.registrar_acesso(self.u, self.d0 + timedelta(days=4))
        self.assertEqual(r3['streak'], 1)
        self.assertEqual(PerfilUsuario.objects.get(usuario=self.u).maior_streak, 2)

    def test_mesmo_dia_nao_paga_duas_vezes(self):
        streak.registrar_acesso(self.u, self.d0)
        self.assertIsNone(streak.registrar_acesso(self.u, self.d0))
        self.assertEqual(coins.saldo(self.u), 1000 + 25)


class TemasTests(TestCase):
    def test_todo_tema_tem_contraste_com_texto_branco(self):
        for nome in ('Flamengo', 'Santos', 'Mirassol', 'Palmeiras', 'Bahia', 'Vitória'):
            tema = tema_para_clube(Clube(nome=nome, cor_hexadecimal='#FFFFFF'))
            self.assertLess(luminosidade(tema['base']), 0.36, nome)

    def test_clube_fora_da_tabela_usa_a_cor_do_admin(self):
        tema = tema_para_clube(Clube(nome='Clube Novo', cor_hexadecimal='#0033AA'))
        self.assertEqual(tema['base'], '#0033aa')

    def test_cor_invalida_cai_no_verde_padrao(self):
        tema = tema_para_clube(Clube(nome='Clube Novo', cor_hexadecimal='azul'))
        self.assertEqual(tema['base'], '#1b5e20')

    def test_sem_clube_devolve_tema_padrao(self):
        self.assertEqual(tema_para_clube(None)['chave'], 'cartolandia')

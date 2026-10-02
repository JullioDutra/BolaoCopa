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


from django.core.cache import cache
from django.urls import reverse

from . import dados, recuperacao


class DadosTests(SimpleTestCase):
    def test_telefone_normaliza_e_valida(self):
        self.assertEqual(dados.normalizar_telefone('(21) 98888-7777'), '5521988887777')
        self.assertEqual(dados.normalizar_telefone('+55 21 98888-7777'), '5521988887777')
        self.assertEqual(dados.normalizar_telefone(''), '')
        for ruim in ('123', '+1 202 555 010099', 'abc'):
            with self.assertRaises(ValueError):
                dados.normalizar_telefone(ruim)
        self.assertEqual(dados.telefone_formatado('5521988887777'), '(21) 98888-7777')

    def test_resposta_ignora_acento_caixa_e_espaco(self):
        h = dados.hash_resposta('Pelé')
        self.assertTrue(dados.resposta_confere('  pele ', h))
        self.assertFalse(dados.resposta_confere('garrincha', h))
        self.assertFalse(dados.resposta_confere('', h))


class RecuperacaoTests(TestCase):
    def setUp(self):
        cache.clear()
        self.u = User.objects.create_user('ana@x.com', email='ana@x.com', password='antiga123', first_name='Ana')
        p = PerfilUsuario.objects.create(usuario=self.u, telefone='5521988887777', pergunta_secreta='craque',
                                         resposta_secreta_hash=dados.hash_resposta('Zico'))

    def test_whatsapp_correto_libera_e_troca_a_senha(self):
        r = self.client.post(reverse('conta:recuperar'), {'email': 'ANA@x.com', 'telefone': '(21) 98888-7777'})
        self.assertEqual(r.status_code, 302)
        url = r['Location']
        r2 = self.client.post(url, {'new_password1': 'SenhaNova#2026x', 'new_password2': 'SenhaNova#2026x'})
        self.assertRedirects(r2, reverse('login'))
        self.u.refresh_from_db()
        self.assertTrue(self.u.check_password('SenhaNova#2026x'))
        # token de uso único
        self.assertEqual(self.client.get(url).status_code, 302)

    def test_pergunta_secreta_libera(self):
        r = self.client.post(reverse('conta:recuperar'), {'email': 'ana@x.com', 'pergunta': 'craque', 'resposta': 'zico'})
        self.assertEqual(r.status_code, 302)

    def test_dado_errado_e_email_inexistente_dao_a_mesma_mensagem(self):
        for email, tel in (('ana@x.com', '(21) 90000-0000'), ('ninguem@x.com', '(21) 98888-7777')):
            r = self.client.post(reverse('conta:recuperar'), {'email': email, 'telefone': tel}, follow=True)
            self.assertContains(r, 'não conferem')

    def test_sem_dado_nenhum_pede_um(self):
        r = self.client.post(reverse('conta:recuperar'), {'email': 'ana@x.com'}, follow=True)
        self.assertContains(r, 'Informe o WhatsApp')

    def test_bloqueia_apos_5_tentativas_mesmo_com_dado_certo(self):
        for _ in range(5):
            self.client.post(reverse('conta:recuperar'), {'email': 'ana@x.com', 'telefone': '(21) 90000-0000'})
        r = self.client.post(reverse('conta:recuperar'), {'email': 'ana@x.com', 'telefone': '(21) 98888-7777'}, follow=True)
        self.assertContains(r, 'Muitas tentativas')

    def test_perfil_sem_dados_cadastrados_nao_e_adivinhavel(self):
        outro = User.objects.create_user('b@x.com', password='x')
        r = self.client.post(reverse('conta:recuperar'), {'email': 'b@x.com', 'telefone': '(21) 98888-7777'}, follow=True)
        self.assertContains(r, 'não conferem')

    def test_token_adulterado_ou_trocado_nao_vale(self):
        self.assertIsNone(recuperacao.usuario_do_token('lixo'))
        token = recuperacao.gerar_token(self.u)
        self.u.set_password('outra'); self.u.save()
        self.assertIsNone(recuperacao.usuario_do_token(token))


class PerfilTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('ana@x.com', email='ana@x.com', password='antiga123', first_name='Ana')
        self.client.force_login(self.u)

    def test_atualiza_dados_e_login_acompanha_o_email(self):
        r = self.client.post(reverse('conta:perfil'), {
            'acao': 'dados', 'nome': 'Aninha', 'email': 'nova@x.com', 'telefone': '(21) 98888-7777',
            'frase': 'Bora!', 'avatar': '🦁', 'avisos_whatsapp': 'on'})
        self.assertEqual(r.status_code, 302)
        self.u.refresh_from_db()
        self.assertEqual((self.u.first_name, self.u.email, self.u.username), ('Aninha', 'nova@x.com', 'nova@x.com'))
        self.assertEqual(self.u.perfil.telefone, '5521988887777')

    def test_email_de_outra_conta_e_recusado(self):
        User.objects.create_user('outro@x.com', email='outro@x.com', password='x')
        r = self.client.post(reverse('conta:perfil'), {'acao': 'dados', 'nome': 'Ana', 'email': 'OUTRO@x.com', 'avatar': '⚽'})
        self.assertContains(r, 'já está em uso')

    def test_bonus_de_perfil_completo_uma_unica_vez(self):
        self.client.post(reverse('conta:perfil'), {'acao': 'dados', 'nome': 'Ana', 'email': 'ana@x.com',
                                                   'telefone': '21988887777', 'avatar': '⚽'})
        self.assertEqual(coins.saldo(self.u), 1000)
        for resp in ('zico', 'pele'):
            self.client.post(reverse('conta:perfil'), {'acao': 'pergunta', 'pergunta': 'craque', 'resposta': resp})
        self.assertEqual(coins.saldo(self.u), 1050)

    def test_troca_de_senha_mantem_logado(self):
        r = self.client.post(reverse('conta:perfil'), {'acao': 'senha', 'old_password': 'antiga123',
                                                      'new_password1': 'Nova#Senha2026', 'new_password2': 'Nova#Senha2026'})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get(reverse('conta:perfil')).status_code, 200)

    def test_abas_renderizam(self):
        for aba in ('dados', 'seguranca'):
            self.assertEqual(self.client.get(reverse('conta:perfil') + f'?aba={aba}').status_code, 200)

    def test_staff_gera_link_de_senha(self):
        self.client.logout()
        staff = User.objects.create_user('staff', password='x', is_staff=True)
        self.client.force_login(staff)
        r = self.client.post(reverse('conta:staff_links_senha'), {'usuario': self.u.pk})
        self.assertContains(r, 'reset-senha/confirmar/')
        self.client.logout(); self.client.force_login(self.u)
        self.assertEqual(self.client.get(reverse('conta:staff_links_senha')).status_code, 302)

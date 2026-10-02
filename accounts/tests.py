from datetime import date, timedelta

from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
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
            'frase': 'Bora!', 'avatar': 'bola', 'avisos_whatsapp': 'on'})
        self.assertEqual(r.status_code, 302)
        self.u.refresh_from_db()
        self.assertEqual((self.u.first_name, self.u.email, self.u.username), ('Aninha', 'nova@x.com', 'nova@x.com'))
        self.assertEqual(self.u.perfil.telefone, '5521988887777')

    def test_email_de_outra_conta_e_recusado(self):
        User.objects.create_user('outro@x.com', email='outro@x.com', password='x')
        r = self.client.post(reverse('conta:perfil'), {'acao': 'dados', 'nome': 'Ana', 'email': 'OUTRO@x.com', 'avatar': 'bola'})
        self.assertContains(r, 'já está em uso')

    def test_bonus_de_perfil_completo_uma_unica_vez(self):
        self.client.post(reverse('conta:perfil'), {'acao': 'dados', 'nome': 'Ana', 'email': 'ana@x.com',
                                                   'telefone': '21988887777', 'avatar': 'bola'})
        self.assertEqual(coins.saldo(self.u), 1000)
        for resp in ('zico', 'pele'):
            self.client.post(reverse('conta:perfil'), {'acao': 'pergunta', 'pergunta': 'craque', 'resposta': resp})
        # +50 do perfil completo e +25 da conquista "Perfil VIP"
        self.assertEqual(coins.saldo(self.u), 1000 + 50 + 25)

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


class NpcTests(TestCase):
    def test_usuario_npc_e_inativo_sem_senha_e_fora_das_listas(self):
        from accounts import npc
        u = npc.criar_usuario_npc('neymar_san', 'Neymar')
        self.assertFalse(u.is_active)
        self.assertFalse(u.has_usable_password())
        self.assertTrue(npc.eh_npc(u))
        self.assertEqual(npc.criar_usuario_npc('neymar_san').pk, u.pk)   # idempotente
        pessoa = User.objects.create_user('ana@x.com', password='x')
        self.assertIn(pessoa, npc.usuarios_reais())
        self.assertNotIn(u, npc.usuarios_reais())

    def test_comando_ajusta_so_quem_nunca_entrou_e_nao_tem_atividade(self):
        import io
        from django.core.management import call_command
        from accounts import npc
        from modocarreira.models import Avatar
        antigo = User.objects.create_user('gabigol_fla')            # criado pelo script antigo
        real = User.objects.create_user('joao@x.com', password='x')  # humano com avatar no carreira
        for usuario in (antigo, real):
            Avatar.objects.create(usuario=usuario, nome_camisa=usuario.username[:20], arquetipo='matador', posicao_preferida='ST',
                                  temporada_nascimento=2026)
        real.last_login = timezone.now()
        real.save()
        out = io.StringIO()
        call_command('ajustar_npcs', stdout=out)
        antigo.refresh_from_db()
        self.assertTrue(antigo.is_active)                      # simulação não grava
        call_command('ajustar_npcs', '--aplicar', stdout=out)
        antigo.refresh_from_db(); real.refresh_from_db()
        self.assertFalse(antigo.is_active)
        self.assertTrue(npc.eh_npc(antigo))
        self.assertTrue(real.is_active)                        # pessoa de verdade fica intacta
        self.assertFalse(npc.eh_npc(real))

    def test_painel_da_staff_esconde_npcs(self):
        from accounts import npc
        npc.criar_usuario_npc('vinijr_fla', 'Vini Jr')
        staff = User.objects.create_user('chefe', password='x', is_staff=True, is_superuser=True, first_name='Chefe')
        self.client.force_login(staff)
        r = self.client.get(reverse('gestao:usuarios'))
        self.assertNotContains(r, 'Vini Jr')
        self.assertContains(self.client.get(reverse('gestao:usuarios') + '?f=npcs'), 'Vini Jr')
        self.assertContains(self.client.get(reverse('gestao:hub')), 'NPCs do carreira')
        self.assertEqual(self.client.get('/admin/auth/user/').status_code, 200)


class AvataresEPerfilPublicoTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('ana@x.com', password='x', first_name='Ana')
        self.o = User.objects.create_user('beto@x.com', password='x', first_name='Beto')
        self.client.force_login(self.u)

    def test_catalogo_codigos_curtos_e_unicos(self):
        from accounts import avatares
        cat = avatares.catalogo()
        self.assertTrue(all(len(c) <= 8 for c in cat), [c for c in cat if len(c) > 8])
        self.assertEqual(len(cat), len(set(cat)))
        from avisos.conquistas import CATALOGO
        self.assertEqual(set(avatares.POR_CONQUISTA) - set(CATALOGO), set())    # nenhuma conquista inexistente
        self.assertEqual(set(CATALOGO) - set(avatares.POR_CONQUISTA), set())    # toda conquista libera um avatar

    def test_emoji_antigo_vira_avatar_padrao(self):
        from accounts import avatares
        self.assertEqual(avatares.normalizar('🦁'), avatares.PADRAO)
        self.assertEqual(avatares.info('xxx')['codigo'], avatares.PADRAO)

    def test_so_usa_avatar_desbloqueado(self):
        from accounts import avatares
        from avisos.models import Conquista
        dados = {'acao': 'dados', 'nome': 'Ana', 'email': 'ana@x.com', 'avatar': 'mundo'}
        r = self.client.post(reverse('conta:perfil'), dados)
        self.assertContains(r, 'bloqueado')
        self.u.perfil.refresh_from_db() if hasattr(self.u, 'perfil') else None
        self.assertNotEqual(PerfilUsuario.objects.filter(usuario=self.u, avatar='mundo').count(), 1)
        Conquista.objects.create(usuario=self.u, slug='campeao_mundo')
        self.assertIn('mundo', avatares.liberados(self.u))
        r = self.client.post(reverse('conta:perfil'), dados)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(PerfilUsuario.objects.get(usuario=self.u).avatar, 'mundo')
        self.assertContains(self.client.get(reverse('conta:perfil')), 'fa-earth-americas')

    def test_perfil_publico(self):
        from avisos.models import Conquista
        Conquista.objects.create(usuario=self.o, slug='cravador')
        r = self.client.get(reverse('conta:perfil_publico', args=[self.o.pk]))
        self.assertContains(r, 'Beto')
        self.assertContains(r, 'Cravador')
        self.assertNotContains(r, 'beto@x.com')               # nada de e-mail/telefone
        self.assertEqual(self.client.get(reverse('conta:perfil_publico', args=[self.u.pk])).status_code, 200)
        self.client.logout()
        self.assertEqual(self.client.get(reverse('conta:perfil_publico', args=[self.o.pk])).status_code, 302)

    def test_perfil_publico_nao_mostra_npc_nem_inativo(self):
        from accounts import npc
        n = npc.criar_usuario_npc('neymar_san', 'Neymar')
        self.assertEqual(self.client.get(reverse('conta:perfil_publico', args=[n.pk])).status_code, 404)
        self.o.is_active = False
        self.o.save()
        self.assertEqual(self.client.get(reverse('conta:perfil_publico', args=[self.o.pk])).status_code, 404)

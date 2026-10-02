from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts import coins


class GestaoTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user('chefe', password='x', is_staff=True, is_superuser=True)
        self.p = User.objects.create_user('zeca', password='x', first_name='Zeca', email='z@x.com')
        self.client.force_login(self.staff)

    def post(self, **dados):
        return self.client.post(reverse('gestao:usuario', args=[self.p.pk]), dados)

    def test_so_staff_acessa(self):
        self.client.force_login(self.p)
        for nome in ('hub', 'usuarios', 'auditoria', 'sistema'):
            self.assertEqual(self.client.get(reverse(f'gestao:{nome}')).status_code, 302)

    def test_paginas_abrem(self):
        for nome in ('hub', 'usuarios', 'auditoria', 'sistema'):
            self.assertEqual(self.client.get(reverse(f'gestao:{nome}')).status_code, 200, nome)
        self.assertEqual(self.client.get(reverse('gestao:usuario', args=[self.p.pk])).status_code, 200)
        self.assertContains(self.client.get(reverse('gestao:usuarios') + '?q=zeca&f=ativos'), 'Zeca')

    def test_editar_cadastro_e_telefone(self):
        self.post(acao='editar', first_name='José', last_name='Silva', email='j@x.com', telefone='+55 (11) 99999-0000', frase='Vamo')
        self.p.refresh_from_db()
        self.assertEqual((self.p.first_name, self.p.email), ('José', 'j@x.com'))
        self.assertEqual(self.p.perfil.telefone, '5511999990000')

    def test_gerar_link_de_senha(self):
        r = self.post(acao='link_senha')
        self.assertContains(r, 'id="linkGerado"')

    def test_ajuste_de_coins_exige_motivo_e_nao_deixa_negativar(self):
        saldo = coins.saldo(self.p)
        self.post(acao='coins', valor='50', motivo='')
        self.assertEqual(coins.saldo(self.p), saldo)
        self.post(acao='coins', valor='50', motivo='prêmio')
        self.assertEqual(coins.saldo(self.p), saldo + 50)
        self.post(acao='coins', valor='-99999', motivo='teste')
        self.assertEqual(coins.saldo(self.p), saldo + 50)

    def test_desativar_e_auditoria(self):
        self.post(acao='desativar')
        self.p.refresh_from_db()
        self.assertFalse(self.p.is_active)
        self.assertTrue(LogEntry.objects.filter(change_message__startswith='[gestão] desativou').exists())
        self.assertContains(self.client.get(reverse('gestao:auditoria')), 'desativou')

    def test_nao_desativa_a_si_mesmo_nem_promove_sem_ser_superuser(self):
        self.client.post(reverse('gestao:usuario', args=[self.staff.pk]), {'acao': 'desativar'})
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active)
        comum = User.objects.create_user('mod', password='x', is_staff=True)
        self.client.force_login(comum)
        self.post(acao='alternar_staff')
        self.p.refresh_from_db()
        self.assertFalse(self.p.is_staff)

    def test_senha_temporaria_so_superuser(self):
        r = self.post(acao='senha_temporaria')
        self.assertContains(r, 'Senha temporária')
        self.p.refresh_from_db()
        self.assertFalse(self.p.check_password('x'))

    def test_tarefa_baralho_no_sistema(self):
        r = self.client.post(reverse('gestao:sistema'), {'acao': 'baralho'})
        self.assertContains(r, 'cartas criadas')

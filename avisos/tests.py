import json
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import PerfilUsuario
from palpites.models import Jogo, Palpite

from . import servico, whatsapp
from .models import Notificacao, PushSubscription


def chaves_de_teste():
    """ Par VAPID real + uma assinatura de navegador válida (para exercitar a criptografia do pywebpush). """
    import base64
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from py_vapid import Vapid
    v = Vapid()
    v.generate_keys()
    b64 = lambda b: base64.urlsafe_b64encode(b).decode().rstrip('=')
    privada = b64(v.private_key.private_numbers().private_value.to_bytes(32, 'big'))
    publica = b64(v.public_key.public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
    cliente = ec.generate_private_key(ec.SECP256R1())
    p256dh = b64(cliente.public_key().public_bytes(serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint))
    return publica, privada, p256dh, b64(b'0123456789abcdef')


class NotificarTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('ana', password='x', first_name='Ana')

    def test_cria_aviso_e_e_idempotente_por_chave(self):
        self.assertIsNotNone(servico.notificar(self.u, 'Oi', 'x', chave='k1'))
        self.assertIsNone(servico.notificar(self.u, 'Oi de novo', 'x', chave='k1'))
        self.assertEqual(Notificacao.objects.count(), 1)
        servico.notificar(self.u, 'Sem chave', 'x')
        servico.notificar(self.u, 'Sem chave 2', 'x')
        self.assertEqual(Notificacao.objects.count(), 3)

    def test_sem_vapid_nao_tenta_push_e_nao_quebra(self):
        PushSubscription.objects.create(usuario=self.u, endpoint='https://push.example/abc', p256dh='x', auth='y')
        with override_settings(VAPID_PUBLIC_KEY=None, VAPID_PRIVATE_KEY=None):
            self.assertIsNotNone(servico.notificar(self.u, 'Oi'))
            self.assertFalse(servico.vapid_configurado())

    def test_push_real_criptografa_e_envia(self):
        publica, privada, p256dh, auth = chaves_de_teste()
        sub = PushSubscription.objects.create(usuario=self.u, endpoint='https://push.example/abc', p256dh=p256dh, auth=auth)
        resposta = mock.Mock(status_code=201, text='ok')
        with override_settings(VAPID_PUBLIC_KEY=publica, VAPID_PRIVATE_KEY=privada, VAPID_EMAIL='mailto:a@b.com'), \
                mock.patch('requests.post', return_value=resposta) as post:
            servico.notificar(self.u, 'Gol!', 'Flamengo 1 x 0', url='/palpites/jogos/')
        self.assertEqual(post.call_count, 1)
        args, kwargs = post.call_args
        self.assertEqual(args[0], 'https://push.example/abc')
        self.assertIn('vapid', kwargs['headers']['authorization'].lower())
        sub.refresh_from_db()
        self.assertIsNotNone(sub.ultimo_envio_ok)

    def test_assinatura_morta_e_removida(self):
        publica, privada, p256dh, auth = chaves_de_teste()
        PushSubscription.objects.create(usuario=self.u, endpoint='https://push.example/morta', p256dh=p256dh, auth=auth)
        morta = mock.Mock(status_code=410, text='gone')
        with override_settings(VAPID_PUBLIC_KEY=publica, VAPID_PRIVATE_KEY=privada), mock.patch('requests.post', return_value=morta):
            servico.notificar(self.u, 'x')
        self.assertFalse(PushSubscription.objects.exists())


class ViewsAvisosTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('ana', password='x', first_name='Ana')
        self.client.force_login(self.u)

    def test_central_lista_e_marca_como_lida(self):
        servico.notificar(self.u, 'Aviso 1')
        r = self.client.get(reverse('avisos:central'))
        self.assertContains(r, 'Aviso 1')
        self.assertFalse(Notificacao.objects.filter(lida=False).exists())

    def test_inscrever_e_cancelar_push(self):
        corpo = {'endpoint': 'https://push.example/xyz', 'keys': {'p256dh': 'a', 'auth': 'b'}}
        r = self.client.post(reverse('avisos:api_inscrever'), json.dumps(corpo), content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(PushSubscription.objects.get().usuario, self.u)
        self.client.post(reverse('avisos:api_cancelar'), json.dumps({'endpoint': corpo['endpoint']}), content_type='application/json')
        self.assertFalse(PushSubscription.objects.exists())

    def test_inscricao_invalida_ou_http_e_recusada(self):
        for corpo in ({'endpoint': 'http://inseguro/x', 'keys': {'p256dh': 'a', 'auth': 'b'}}, {'endpoint': 'https://x'}, 'lixo'):
            r = self.client.post(reverse('avisos:api_inscrever'), json.dumps(corpo), content_type='application/json')
            self.assertEqual(r.status_code, 400)

    def test_inscrever_exige_login(self):
        self.client.logout()
        self.assertEqual(self.client.post(reverse('avisos:api_inscrever'), '{}', content_type='application/json').status_code, 302)

    def test_service_worker_na_raiz_com_escopo(self):
        r = self.client.get('/sw.js')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Service-Worker-Allowed'], '/')
        self.assertIn(b'addEventListener', r.content)
        self.assertIn(b"'push'", r.content)

    def test_testar_cria_aviso(self):
        self.client.post(reverse('avisos:testar'))
        self.assertTrue(Notificacao.objects.filter(tipo='teste').exists())

    def test_staff_painel_so_para_staff_e_envia_para_todos(self):
        outro = User.objects.create_user('bia', password='x')
        self.assertEqual(self.client.get(reverse('avisos:staff')).status_code, 302)
        self.u.is_staff = True
        self.u.save()
        PerfilUsuario.objects.create(usuario=outro, telefone='5521988887777')
        jogo = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=timezone.now() + timedelta(days=2))
        r = self.client.get(reverse('avisos:staff'))
        self.assertContains(r, 'wa.me/5521988887777')
        self.assertContains(r, 'Flamengo x Palmeiras')
        self.client.post(reverse('avisos:staff'), {'titulo': 'Rodada aberta!', 'texto': 'Bora', 'url': 'https://malicioso.com'})
        self.assertEqual(Notificacao.objects.filter(titulo='Rodada aberta!').count(), 2)
        self.assertEqual(Notificacao.objects.filter(titulo='Rodada aberta!').first().url, '/')      # só caminhos internos

    def test_sino_mostra_contagem(self):
        servico.notificar(self.u, 'Novo')
        self.assertContains(self.client.get(reverse('futebol:hub')), 'bg-danger')


class LembretesTests(TestCase):
    def setUp(self):
        self.ana = User.objects.create_user('ana', password='x')
        self.bia = User.objects.create_user('bia', password='x')

    def test_lembrete_so_para_quem_nao_palpitou_e_nao_repete(self):
        jogo = Jogo.objects.create(time_casa='A', time_fora='B', data_hora=timezone.now() + timedelta(hours=2))
        Palpite.objects.create(usuario=self.ana, jogo=jogo, gols_casa=1, gols_fora=0)
        call_command('enviar_lembretes', verbosity=0)
        call_command('enviar_lembretes', verbosity=0)
        avisos = Notificacao.objects.filter(tipo='lembrete')
        self.assertEqual([a.usuario for a in avisos], [self.bia])

    def test_nao_avisa_jogo_longe_ou_ja_fechado(self):
        Jogo.objects.create(time_casa='A', time_fora='B', data_hora=timezone.now() + timedelta(days=2))
        Jogo.objects.create(time_casa='C', time_fora='D', data_hora=timezone.now() + timedelta(minutes=30))     # já fechou (1h antes)
        call_command('enviar_lembretes', verbosity=0)
        self.assertFalse(Notificacao.objects.exists())

    def test_resultado_diferencia_cravada_acerto_e_erro(self):
        jogo = Jogo.objects.create(time_casa='A', time_fora='B', data_hora=timezone.now() - timedelta(hours=3))
        cravou = Palpite.objects.create(usuario=self.ana, jogo=jogo, gols_casa=2, gols_fora=0)
        errou = Palpite.objects.create(usuario=self.bia, jogo=jogo, gols_casa=0, gols_fora=1)
        jogo.gols_casa_real, jogo.gols_fora_real, jogo.finalizado = 2, 0, True
        jogo.save()
        call_command('enviar_lembretes', verbosity=0)
        self.assertEqual(Notificacao.objects.get(usuario=self.ana, tipo='resultado').titulo, '🎯 CRAVOU!')
        self.assertIn('Dessa vez', Notificacao.objects.get(usuario=self.bia, tipo='resultado').titulo)


class WhatsappTests(TestCase):
    def test_links(self):
        self.assertEqual(whatsapp.link_chat('+55 (21) 98888-7777', 'oi & tchau'), 'https://wa.me/5521988887777?text=oi%20%26%20tchau')
        self.assertTrue(whatsapp.link_compartilhar('a b').endswith('?text=a%20b'))

    def test_resumo_traz_ranking_e_jogos(self):
        u = User.objects.create_user('ana', password='x', first_name='Ana')
        jogo = Jogo.objects.create(time_casa='Flamengo', time_fora='Palmeiras', data_hora=timezone.now() + timedelta(days=1))
        texto = whatsapp.texto_resumo([{'usuario': u, 'total_pontos': 42}], [jogo], 'https://x.com')
        for trecho in ('Ana — 42 pts', 'Flamengo x Palmeiras', 'https://x.com', '🥇'):
            self.assertIn(trecho, texto)

    @override_settings(WHATSAPP_GRUPO_URL='https://chat.whatsapp.com/abc')
    def test_dashboard_mostra_botao_do_grupo(self):
        from bolao.models import Participacao
        u = User.objects.create_user('ana', password='x')
        Participacao.objects.create(usuario=u, tipo='resenha')
        self.client.force_login(u)
        self.assertContains(self.client.get(reverse('dashboard')), 'chat.whatsapp.com/abc')


class ConquistasEFeedTests(TestCase):
    def setUp(self):
        self.u = User.objects.create_user('ana', password='x', first_name='Ana')

    def test_desbloqueia_uma_vez_paga_recompensa_avisa_e_publica(self):
        from accounts import coins
        from palpites.models import Palpite
        from . import conquistas
        from .models import Atividade, Conquista
        jogo = Jogo.objects.create(time_casa='A', time_fora='B', data_hora=timezone.now() - timedelta(days=1))
        Palpite.objects.create(usuario=self.u, jogo=jogo, gols_casa=1, gols_fora=0)
        self.assertEqual(conquistas.checar(self.u), ['estreante'])
        self.assertEqual(conquistas.checar(self.u), [])                           # idempotente
        self.assertEqual(coins.saldo(self.u), 1000 + conquistas.RECOMPENSA)
        self.assertTrue(Notificacao.objects.filter(usuario=self.u, tipo='conquista').exists())
        self.assertIn('Estreante', Atividade.objects.get(tipo='conquista').texto)
        self.assertEqual(Conquista.objects.count(), 1)

    def test_regras_de_aposta_zebra_e_banqueiro(self):
        from decimal import Decimal
        from accounts import coins
        from melhores.models import Aposta, Candidato, Categoria, Edicao
        from . import conquistas
        ed = Edicao.objects.create(ano=2026)
        cat = Categoria.objects.create(edicao=ed, slug='x', nome='X')
        cand = Candidato.objects.create(categoria=cat, nome='Y')
        Aposta.objects.create(usuario=self.u, categoria=cat, candidato=cand, valor=10, odd_travada=Decimal('7.00'), status='ganha')
        coins.creditar(self.u, 1500, 'teste')
        novos = set(conquistas.checar(self.u))
        self.assertTrue({'apostador', 'zebreiro', 'banqueiro'} <= novos)

    def test_lista_do_perfil_marca_ganhas(self):
        from . import conquistas
        lista = conquistas.do_usuario(self.u)
        self.assertEqual(len(lista), len(conquistas.CATALOGO))
        self.assertFalse(any(c['ganha'] for c in lista))

    def test_checar_nunca_levanta(self):
        from . import conquistas
        with mock.patch.object(conquistas, '_regras', side_effect=RuntimeError('boom')):
            self.assertEqual(conquistas.checar(self.u), [])

    def test_feed_aparece_no_dashboard_e_na_pagina(self):
        from bolao.models import Participacao
        from . import atividade
        Participacao.objects.create(usuario=self.u, tipo='resenha')
        self.client.force_login(self.u)
        atividade.registrar(self.u, 'cravada', '🎯 Ana cravou Fla 2 x 1 Pal!')
        self.assertContains(self.client.get(reverse('dashboard')), 'Ana cravou Fla 2 x 1 Pal!')
        self.assertContains(self.client.get(reverse('avisos:resenha')), 'Ana cravou Fla 2 x 1 Pal!')

    def test_aposta_e_voto_entram_no_feed(self):
        from django.core.management import call_command
        from futebol.models import Atleta, Time
        from melhores import services
        from melhores.models import Categoria
        from .models import Atividade
        call_command('seed_melhores', '--ano', '2026', verbosity=0)
        cat = Categoria.objects.get(slug='vagabundo')
        with self.captureOnCommitCallbacks(execute=True):
            services.apostar(self.u, cat.id, cat.candidatos.get(nome='Mark').id, 100)
        self.assertTrue(Atividade.objects.filter(tipo='aposta', texto__contains='Ana').exists())

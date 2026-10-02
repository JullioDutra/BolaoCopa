import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from duelos.baralho import atributos, garantir_cartas
from duelos.models import CartaTrunfo, PartidaMiniFanaticos, PartidaTrunfo


class SuperTrunfoTests(TestCase):
    def setUp(self):
        self.a = User.objects.create_user('ana', password='x')
        self.b = User.objects.create_user('beto', password='x')

    def _iniciar(self):
        self.client.force_login(self.a)
        self.client.post(reverse('duelos:criar_trunfo'))
        partida = PartidaTrunfo.objects.get()
        self.client.force_login(self.b)
        self.client.get(reverse('duelos:entrar_trunfo', args=[partida.id]))
        partida.refresh_from_db()
        return partida

    def test_baralho_se_completa_sozinho_e_atributos_sao_estaveis(self):
        self.assertEqual(CartaTrunfo.objects.count(), 0)
        self.assertGreaterEqual(garantir_cartas(10), 10)
        self.assertEqual(atributos('Zico', 'MEI', 96), atributos('Zico', 'MEI', 96))
        self.assertLess(atributos('Cássio', 'GOL', 80)['finalizacao'], atributos('Gabigol', 'ATA', 80)['finalizacao'])

    def test_partida_distribui_cinco_cartas_para_cada(self):
        p = self._iniciar()
        self.assertEqual(p.status, 'andamento')
        self.assertEqual((len(p.baralho_criador), len(p.baralho_convidado)), (4, 4))
        self.assertEqual((p.pontos_criador, p.pontos_convidado), (5, 5))

    def test_jogada_exige_a_vez_e_atributo_valido(self):
        p = self._iniciar()
        url = reverse('duelos:batalhar_trunfo_api', args=[p.id])
        r = self.client.post(url, json.dumps({'atributo': 'rit'}), content_type='application/json')  # beto não tem a vez
        self.assertIn('vez', r.json()['erro'])
        self.client.force_login(self.a)
        r = self.client.post(url, json.dumps({'atributo': 'xxx'}), content_type='application/json')
        self.assertEqual(r.json()['erro'], 'Atributo inválido.')
        self.assertEqual(self.client.get(url).status_code, 405)

    def test_partida_termina_com_vencedor_e_resultado(self):
        p = self._iniciar()
        total = 10
        for _ in range(60):
            p.refresh_from_db()
            if p.status == 'finalizado':
                break
            self.client.force_login(p.turno_de)
            r = self.client.post(reverse('duelos:batalhar_trunfo_api', args=[p.id]),
                                json.dumps({'atributo': 'fis'}), content_type='application/json').json()
            self.assertTrue(r['sucesso'])
        p.refresh_from_db()
        self.assertEqual(p.status, 'finalizado')
        self.assertEqual(p.pontos_criador + p.pontos_convidado, total)
        self.assertEqual(self.client.get(reverse('duelos:resultado_trunfo', args=[p.id])).status_code, 200)

    def test_resultado_antes_do_fim_redireciona(self):
        self.client.force_login(self.a)
        self.client.post(reverse('duelos:criar_trunfo'))
        p = PartidaTrunfo.objects.get()
        r = self.client.get(reverse('duelos:resultado_trunfo', args=[p.id]))
        self.assertEqual(r.status_code, 302)

    def test_status_api_traz_carta_com_clube(self):
        p = self._iniciar()
        dados = self.client.get(reverse('duelos:status_trunfo_api', args=[p.id])).json()
        self.assertIn('clube', dados['minha_carta'])
        self.assertEqual(dados['pontos_meus'], 5)


class MiniFanaticosSemClubesTests(TestCase):
    def test_tela_jogo_sem_clubes_redireciona_em_vez_de_500(self):
        u = User.objects.create_user('ana', password='x')
        self.client.force_login(u)
        self.client.post(reverse('duelos:criar_mini_fanaticos'))
        p = PartidaMiniFanaticos.objects.get()
        r = self.client.get(reverse('duelos:tela_jogo_mini', args=[p.id]))
        self.assertIn(r.status_code, (302, 404))
        self.assertEqual(self.client.get(reverse('duelos:tela_jogo_mini', args=[9999])).status_code, 404)


class ModalFimDeJogoTests(TestCase):
    def _partida(self, tipo, **extra):
        from duelos.models import CategoriaDesafio, PartidaDuelo
        a = User.objects.filter(username='ana').first() or User.objects.create_user('ana', password='x', first_name='Ana')
        b = User.objects.filter(username='beto').first() or User.objects.create_user('beto', password='x', first_name='Beto')
        cat = CategoriaDesafio.objects.create(tipo=tipo, titulo='Flamengo 1981', resposta_oculta='Zico')
        return a, PartidaDuelo.objects.create(categoria=cat, jogador_criador=a, jogador_convidado=b, status='andamento', turno_de=a, **extra)

    def test_modal_padronizado_nos_dois_jogos(self):
        for tipo, esperado in (('elenco', 'Flamengo 1981'), ('trajetoria', 'Zico')):
            a, p = self._partida(tipo)
            self.client.force_login(a)
            r = self.client.get(reverse('duelos:tela_jogo', args=[p.id]))
            self.assertEqual(r.status_code, 200)
            self.assertContains(r, 'id="modalFimJogo"')
            self.assertContains(r, 'fim-placar')                  # placar visível no modal
            self.assertContains(r, 'window.abrirFimDeJogo(data)')
            self.assertContains(r, esperado)
            self.assertNotContains(r, 'fa-whistle')               # ícone inexistente no FontAwesome free
            p.delete()

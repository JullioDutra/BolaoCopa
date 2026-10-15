from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CartaJogador, ElencoHistorico, MeuDraft, PartidaPenalti


class TelaX1Test(TestCase):
    def setUp(self):
        elenco = ElencoHistorico.objects.create(nome='Brasil 2002')
        self.j1 = User.objects.create_user('j1', password='x')
        self.j2 = User.objects.create_user('j2', password='x')
        drafts = []
        for usuario, base in ((self.j1, 0), (self.j2, 10)):
            draft = MeuDraft.objects.create(usuario=usuario, goleiro=CartaJogador.objects.create(
                nome=f'Goleiro {base}', elenco=elenco, posicao='goleiro', over=85))
            draft.batedores.set([CartaJogador.objects.create(nome=f'Batedor {base + i}', elenco=elenco,
                                                             posicao='atacante', over=80 + i) for i in range(5)])
            drafts.append(draft)
        self.partida = PartidaPenalti.objects.create(jogador1=self.j1, jogador2=self.j2, draft_j1=drafts[0],
                                                     draft_j2=drafts[1], fase='5_cobrancas', turno_batedor=self.j1)

    def test_tela_traz_campo_2d_e_zonas_clicaveis(self):
        self.client.force_login(self.j1)
        resp = self.client.get(reverse('minijogo:tela_jogo', args=[self.partida.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="campo2d"')
        self.assertContains(resp, 'window.Campo2D')
        for zona in ('se', 'me', 'sd', 'ie', 'mc', 'id'):
            self.assertContains(resp, f'id="zona-{zona}"')

    def test_status_devolve_dados_da_animacao(self):
        self.partida.ultimo_chute_zona, self.partida.ultima_defesa_zona, self.partida.ultimo_resultado = 'se', 'mc', 'gol'
        self.partida.save()
        self.client.force_login(self.j2)
        dados = self.client.get(reverse('minijogo:api_status_partida', args=[self.partida.id])).json()
        self.assertEqual((dados['ultimo_chute_zona'], dados['ultima_defesa_zona'], dados['ultimo_resultado']), ('se', 'mc', 'gol'))
        self.assertEqual(dados['meu_turno'], 'defender')

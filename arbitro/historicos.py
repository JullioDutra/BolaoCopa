"""
Lances reais e famosos de Copas do Mundo. O jogador apita como se estivesse lá;
a explicação conta o que o árbitro fez de verdade e o que a regra manda.

As posições na cena são uma reconstrução aproximada do lance (não é tracking
oficial), mas preservam o que decide a jogada: a margem do impedimento, onde a
bola estava em relação à linha, onde foi o contato.
"""
from .base import (cena_campo, cena_linha, g_cartao, g_gol, g_impedimento, g_marcacao, g_validar, grupo,
                   jogador as J)

ARG = {'a': '#7dd3fc'}
BRA = {'a': '#facc15'}


def _lances():
    return [
        {
            'chave': 'lampard-2010', 'categoria': 'linha',
            'titulo': 'Copa 2010 · Alemanha x Inglaterra',
            'contexto': 'Oitavas de final, em Bloemfontein. A Alemanha vence por 2 a 1 quando Frank Lampard '
                        'chuta de fora da área: a bola bate no travessão, quica no chão e volta para o campo.',
            'pergunta': 'Foi gol?',
            'grupos': [g_gol()], 'correta': {'decisao': 'gol'},
            'explicacao': 'Foi gol, e com folga: a bola quicou claramente depois da linha. O uruguaio Jorge Larrionda '
                          'e o assistente não viram, e a Alemanha venceu por 4 a 1. O lance pressionou a FIFA a '
                          'adotar a tecnologia da linha do gol, que estreou em Copas em 2014.',
            'cena': cena_linha(68, 'gol', -8, 'quique'),
            'var': {'zoom': True, 'dica': 'A bola inteira precisa ultrapassar a linha inteira. Compare a borda da bola '
                                          'mais próxima do campo com a borda da linha do lado do gol.'},
        },
        {
            'chave': 'hurst-1966', 'categoria': 'linha',
            'titulo': 'Final da Copa 1966 · Inglaterra x Alemanha Ocidental',
            'contexto': 'Prorrogação em Wembley, 2 a 2. Geoff Hurst gira e chuta forte: a bola explode no travessão, '
                        'cai perto da linha e é afastada pela defesa alemã.',
            'pergunta': 'A bola entrou inteira? Foi gol?',
            'grupos': [g_gol()], 'correta': {'decisao': 'nao_gol'},
            'explicacao': 'O bandeirinha Tofiq Bahramov indicou gol e a Inglaterra foi campeã por 4 a 2. Um estudo da '
                          'Universidade de Oxford (1995), analisando as imagens, concluiu que a bola não ultrapassou '
                          'totalmente a linha: pela regra, não era gol.',
            'cena': cena_linha(13, 'gol', 10, 'quique'),
            'var': {'zoom': True, 'dica': 'A linha faz parte do gol? Não: só é gol quando a bola inteira passa da linha inteira.'},
        },
        {
            'chave': 'mitoma-2022', 'categoria': 'linha',
            'titulo': 'Copa 2022 · Japão x Espanha',
            'contexto': 'Fase de grupos, 1 a 1. Mitoma se estica na linha de fundo e cruza; Ao Tanaka empurra para o gol. '
                        'Da arquibancada, parecia que a bola já tinha saído.',
            'pergunta': 'A bola saiu antes do cruzamento?',
            'grupos': [grupo('decisao', 'Decisão', ('saiu', 'Saiu: anular o gol'), ('em_jogo', 'Em jogo: gol válido'))],
            'correta': {'decisao': 'em_jogo'},
            'explicacao': 'O VAR confirmou o gol: vista de cima, uma parte da curvatura da bola ainda estava sobre a linha. '
                          'Para sair, a bola inteira precisa passar da linha inteira. O Japão venceu por 2 a 1 e '
                          'terminou líder do grupo.',
            'cena': cena_linha(21.5, 'fundo', -5, 'rasteira'),
            'var': {'zoom': True, 'dica': 'Olhe de cima: alguma parte da bola ainda está sobre a linha?'},
        },
        {
            'chave': 'benzema-2014', 'categoria': 'linha',
            'titulo': 'Copa 2014 · França x Honduras',
            'contexto': 'Benzema chuta cruzado, a bola bate na trave, corre pela linha e volta nas mãos do goleiro '
                        'Valladares, que tenta segurá-la.',
            'pergunta': 'Foi gol?',
            'grupos': [g_gol()], 'correta': {'decisao': 'gol'},
            'explicacao': 'Gol (contra, de Valladares). Foi o primeiro gol da história das Copas confirmado pela '
                          'tecnologia da linha do gol: o relógio do árbitro Sandro Ricci vibrou com o aviso.',
            'cena': cena_linha(34, 'gol', 25, 'rasteira'),
            'var': {'zoom': True, 'dica': 'A bola inteira precisa ultrapassar a linha inteira.'},
        },
        {
            'chave': 'mao-de-deus-1986', 'categoria': 'mao',
            'titulo': 'Copa 1986 · Argentina x Inglaterra',
            'contexto': 'Quartas de final, no Azteca. Uma bola espirrada sobe na área inglesa; Maradona salta junto '
                        'com o goleiro Shilton, bem mais alto que ele, e a bola entra.',
            'pergunta': 'O gol vale?',
            'grupos': [g_validar()], 'correta': {'decisao': 'anular'},
            'explicacao': 'Maradona tocou a bola com a mão: a “Mão de Deus”. O tunisiano Ali Bin Nasser validou e a '
                          'Argentina venceu por 2 a 1, rumo ao título. Correto: anular o gol, tiro livre direto para a '
                          'Inglaterra e amarelo por tentar marcar com a mão.',
            'cena': cena_campo([80, 14, 108, 54], [
                J('a', 10, (99.6, 33.2), de=(97.5, 33.5), ate=(101, 33), nome='Maradona', foco=True),
                J('g', 1, (100.4, 33.8), de=(102.5, 34), ate=(101.3, 34.5), nome='Shilton'),
                J('d', 6, (98, 37), de=(95, 38), ate=(99, 37)),
                J('a', 11, (93, 26), de=(91, 27), ate=(94, 27)),
                J('d', 3, (96, 28), de=(94, 29), ate=(97, 29)),
            ], ((90, 30), (99.8, 33.1), (105.6, 33.8)), 'TOQUE NA BOLA', mao=(99.8, 33.1), cores=ARG),
            'var': {'zoom': {'x': 99.8, 'y': 33.2, 'r': 3.5}, 'dica': 'Gol marcado com a mão, mesmo sem querer, é sempre anulado.'},
        },
        {
            'chave': 'henry-2009', 'categoria': 'mao',
            'titulo': 'Repescagem 2009 · França x Irlanda',
            'contexto': 'Prorrogação, vaga na Copa 2010 em jogo. Uma bola longa cai perto da linha de fundo; Thierry Henry '
                        'a domina e cruza para Gallas marcar de cabeça.',
            'pergunta': 'O gol vale?',
            'grupos': [g_validar()], 'correta': {'decisao': 'anular'},
            'explicacao': 'Henry ajeitou a bola com a mão antes do cruzamento, e o gol foi validado pelo sueco Martin '
                          'Hansson. A França foi à Copa e o lance virou escândalo. Correto: anular e dar tiro livre '
                          'para a Irlanda (mão deliberada também dá amarelo).',
            'cena': cena_campo([78, 14, 108, 58], [
                J('a', 12, (103.8, 46), de=(101, 47), ate=(104, 44.5), nome='Henry', foco=True),
                J('d', 5, (102.4, 45), de=(100, 45), ate=(103, 44)),
                J('a', 5, (100.5, 36.5), de=(97, 38), ate=(101.5, 35.5), nome='Gallas'),
                J('d', 4, (99, 38), de=(96, 39), ate=(100.5, 37)),
                J('g', 1, (103.5, 35), de=(104, 34), ate=(103, 36.5)),
            ], ((70, 32), (103.9, 45.8), [(101.6, 35.6), (105.6, 34.6)]), 'DOMÍNIO DE HENRY', mao=(103.9, 45.6)),
            'var': {'zoom': {'x': 103.8, 'y': 45.8, 'r': 3.5}, 'dica': 'Olhe com o que Henry controla a bola antes de cruzar.'},
        },
        {
            'chave': 'suarez-2010', 'categoria': 'mao',
            'titulo': 'Copa 2010 · Uruguai x Gana',
            'contexto': 'Quartas de final, último minuto da prorrogação, 1 a 1. Adiyiah cabeceia para o gol vazio e Luis '
                        'Suárez, em cima da linha, tira a bola com as mãos.',
            'pergunta': 'Qual a marcação e o cartão?',
            'grupos': [g_marcacao(), g_cartao()], 'correta': {'marcacao': 'penalti', 'cartao': 'vermelho'},
            'explicacao': 'O português Olegário Benquerença acertou: pênalti e vermelho, porque a mão impediu um gol. '
                          'Gyan bateu no travessão e o Uruguai venceu nos pênaltis.',
            'cena': cena_campo([84, 14, 108, 54], [
                J('a', 23, (99.5, 30), de=(97.5, 30.5), ate=(100.5, 31), nome='Adiyiah', foco=True),
                J('d', 9, (104.5, 34.6), de=(104, 36), ate=(104.2, 35.5), nome='Suárez', toque=True),
                J('d', 2, (101, 33), de=(100, 33), ate=(102, 34)),
                J('g', 1, (102.5, 28), de=(103.5, 31), ate=(102, 27)),
            ], ((96, 25), (104.6, 34.2), (100, 42)), 'NA LINHA DO GOL', mao=(104.6, 34.2)),
            'var': {'zoom': {'x': 104.4, 'y': 34.4, 'r': 3}, 'dica': 'Mão que impede um gol é infração com punição máxima de cartão.'},
        },
        {
            'chave': 'de-jong-2010', 'categoria': 'cartao',
            'titulo': 'Final da Copa 2010 · Holanda x Espanha',
            'contexto': 'Aos 28 minutos, Xabi Alonso domina uma bola alta no meio-campo. Nigel de Jong chega atrasado, '
                        'com a sola da chuteira, e acerta o peito do espanhol.',
            'pergunta': 'Qual a marcação e o cartão?',
            'grupos': [g_marcacao(), g_cartao()], 'correta': {'marcacao': 'falta', 'cartao': 'vermelho'},
            'explicacao': 'Howard Webb deu só amarelo. Uma entrada com a sola no peito, com força excessiva, é jogada brusca '
                          'grave: vermelho direto e tiro livre para a Espanha, que acabou campeã.',
            'cena': cena_campo([34, 10, 70, 52], [
                J('a', 14, (50, 30), de=(48, 29), ate=(50.6, 31.2), nome='Xabi Alonso', foco=True, cai=True),
                J('d', 8, (49.4, 30.6), de=(45.5, 33.5), ate=(50.2, 30.6), nome='De Jong'),
                J('a', 16, (44, 20), de=(43, 21), ate=(45, 21)),
                J('d', 10, (55, 36), de=(56, 37), ate=(54, 35)),
            ], ((38, 18), (50, 30), (51.5, 33)), 'CONTATO', contato=(49.7, 30.2), cores={'a': '#dc2626', 'd': '#f97316'}),
            'var': {'zoom': {'x': 49.8, 'y': 30.3, 'r': 4}, 'dica': 'Entrada que põe em risco a integridade do adversário é jogada brusca grave.'},
        },
        {
            'chave': 'zidane-2006', 'categoria': 'conduta',
            'titulo': 'Final da Copa 2006 · Itália x França',
            'contexto': 'Prorrogação, 1 a 1. Longe da bola, depois de uma troca de palavras, Zidane se vira e dá uma '
                        'cabeçada no peito de Materazzi.',
            'pergunta': 'Que cartão Zidane merece?',
            'grupos': [g_cartao()], 'correta': {'cartao': 'vermelho'},
            'explicacao': 'O argentino Horacio Elizondo expulsou Zidane após o aviso do quarto árbitro. Agressão é conduta '
                          'violenta: vermelho direto, com a bola em jogo ou não. A Itália foi campeã nos pênaltis.',
            'cena': cena_campo([38, 8, 76, 52], [
                J('a', 10, (57.4, 31.8), de=(55, 29.5), ate=(57.2, 31.4), nome='Zidane', foco=True),
                J('d', 23, (58.1, 32.4), de=(58.6, 31), ate=(59.4, 33.6), nome='Materazzi', cai=True),
                J('a', 12, (49, 22), de=(50, 23), ate=(49, 22)),
                J('d', 5, (63, 40), de=(63, 40), ate=(62, 39)),
            ], ((30, 12), (34, 14), (37, 15)), 'CABEÇADA', contato=(57.8, 32.1),
                cores={'a': '#f8fafc', 'd': '#1d4ed8'}),
            'var': {'dica': 'Agressão a um adversário é conduta violenta, esteja a bola onde estiver.'},
        },
        {
            'chave': 'schumacher-1982', 'categoria': 'conduta',
            'titulo': 'Copa 1982 · Alemanha Ocidental x França',
            'contexto': 'Semifinal em Sevilha. Battiston sai cara a cara e toca por cima; o goleiro Schumacher sai '
                        'voando, sem chance de alcançar a bola, e acerta o francês em cheio com o corpo.',
            'pergunta': 'Que cartão o goleiro merece?',
            'grupos': [g_cartao()], 'correta': {'cartao': 'vermelho'},
            'explicacao': 'Battiston perdeu dentes, teve vértebra lesionada e saiu desacordado. O holandês Charles Corver '
                          'não deu nem falta (tiro de meta). Um choque assim, sem disputar a bola e com força excessiva, '
                          'é vermelho direto.',
            'cena': cena_campo([74, 12, 108, 56], [
                J('a', 3, (94.8, 34), de=(85, 34), ate=(96.8, 35.2), nome='Battiston', foco=True, cai=True),
                J('g', 1, (95.4, 34.3), de=(101.5, 34), ate=(96.4, 34.6), nome='Schumacher'),
                J('d', 4, (88, 28), de=(84, 28), ate=(91, 29)),
            ], ((82, 30), (94.6, 34), (105.8, 39)), 'CHOQUE', contato=(95.1, 34.1),
                cores={'a': '#1d4ed8', 'd': '#f8fafc', 'g': '#16a34a'}),
            'var': {'dica': 'O goleiro não tentou jogar a bola e usou força excessiva.'},
        },
        {
            'chave': 'lautaro-2022', 'categoria': 'impedimento',
            'titulo': 'Copa 2022 · Argentina x Arábia Saudita',
            'contexto': 'A defesa saudita adianta a linha a todo momento. Lautaro Martínez arranca nas costas dos '
                        'zagueiros, recebe o passe em profundidade e toca na saída do goleiro.',
            'pergunta': 'Lautaro (destacado) estava impedido no momento do passe?',
            'grupos': [g_impedimento()], 'correta': {'decisao': 'impedido'},
            'explicacao': 'O impedimento semiautomático mostrou o ombro de Lautaro à frente do penúltimo defensor: gol '
                          'anulado. A Arábia Saudita virou e venceu por 2 a 1, uma das maiores zebras das Copas.',
            'cena': cena_campo([56, 0, 108, 68], [
                J('a', 22, (80.3, 30), de=(78, 30.5), ate=(92, 33), nome='Lautaro', foco=True),
                J('a', 10, (64, 38), de=(62, 39), ate=(65, 38), nome='Messi'),
                J('d', 5, (80, 24), de=(79, 24), ate=(82.5, 25)),
                J('d', 4, (79.6, 36), de=(78.6, 36), ate=(82, 36)),
                J('d', 3, (79.2, 14), de=(78, 14), ate=(81, 15)),
                J('d', 2, (78.7, 50), de=(77.6, 50), ate=(80.5, 49)),
                J('g', 21, (100.5, 34), de=(101, 34), ate=(98, 33.5)),
            ], ((61, 39), (64.2, 38), (92.5, 33)), 'MOMENTO DO PASSE', cores=ARG),
            'var': {'linhas': [{'x': 80.0, 't': 'd'}, {'x': 80.3, 't': 'a'}],
                    'dica': 'Compare o atacante com o penúltimo defensor (o goleiro conta) no momento do passe.'},
        },
        {
            'chave': 'tevez-2010', 'categoria': 'impedimento',
            'titulo': 'Copa 2010 · Argentina x México',
            'contexto': 'Oitavas de final. O goleiro mexicano sai do gol, Messi alcança a bola na área e toca para Tevez, '
                        'que cabeceia para a rede.',
            'pergunta': 'Tevez (destacado) estava impedido no momento do passe?',
            'grupos': [g_impedimento()], 'correta': {'decisao': 'impedido'},
            'explicacao': 'Tevez estava claramente impedido, mas o italiano Roberto Rosetti validou. O telão do estádio '
                          'reprisou o lance e os mexicanos cercaram a arbitragem. A Argentina venceu por 3 a 1.',
            'cena': cena_campo([76, 8, 108, 60], [
                J('a', 11, (100.6, 35.5), de=(99.5, 35), ate=(101.6, 35), nome='Tevez', foco=True),
                J('a', 10, (96.4, 29), de=(94, 30), ate=(96.8, 29.5), nome='Messi'),
                J('g', 1, (96.6, 31.5), de=(100, 33), ate=(97.4, 32.5), nome='Pérez'),
                J('d', 4, (95.6, 37.6), de=(94, 38), ate=(97.5, 37)),
                J('d', 2, (93.5, 26.5), de=(92.5, 26), ate=(95, 27.5)),
            ], ((90, 26), (96.5, 29.2), [(100.6, 35.4), (105.6, 34.4)]), 'MOMENTO DO PASSE', cores=ARG),
            'var': {'linhas': [{'x': 96.6, 't': 'd'}, {'x': 100.6, 't': 'a'}],
                    'dica': 'Com o goleiro fora do gol, quem é o penúltimo defensor?'},
        },
        {
            'chave': 'griezmann-2018', 'categoria': 'area',
            'titulo': 'Copa 2018 · França x Austrália',
            'contexto': 'Griezmann recebe em velocidade, entra na área e Risdon dá um carrinho por trás. O árbitro manda '
                        'o jogo seguir.',
            'pergunta': 'Qual a marcação?',
            'grupos': [g_marcacao()], 'correta': {'marcacao': 'penalti'},
            'explicacao': 'Depois de revisar no monitor, o uruguaio Andrés Cunha deu o pênalti: Risdon acertou o pé de '
                          'Griezmann sem tocar na bola. Foi o primeiro pênalti da história das Copas marcado com o VAR.',
            'cena': cena_campo([76, 10, 108, 60], [
                J('a', 7, (96.5, 40), de=(87, 45), ate=(98.2, 39), nome='Griezmann', foco=True, cai=True),
                J('d', 19, (96.2, 40.7), de=(92, 47), ate=(97, 41.4), nome='Risdon'),
                J('g', 1, (103, 35.5), de=(103.5, 34.5), ate=(102.5, 37)),
                J('d', 4, (99, 31), de=(97, 33), ate=(100, 32)),
            ], ((86, 45.5), (96.7, 39.8), (99.5, 38.5)), 'CONTATO', contato=(96.6, 40.4),
                cores={'a': '#1d4ed8', 'd': '#facc15'}),
            'var': {'zoom': {'x': 96.6, 'y': 40.4, 'r': 3.5}, 'dica': 'O defensor tocou primeiro a bola ou o pé do atacante?'},
        },
        {
            'chave': 'di-maria-2022', 'categoria': 'area',
            'titulo': 'Final da Copa 2022 · Argentina x França',
            'contexto': 'Aos 21 minutos, Di María corta da esquerda para dentro da área. Dembélé chega por trás, sem '
                        'alcançar a bola, e encosta no argentino, que cai.',
            'pergunta': 'Qual a marcação?',
            'grupos': [g_marcacao()], 'correta': {'marcacao': 'penalti'},
            'explicacao': 'O polonês Szymon Marciniak marcou e Messi converteu. Carga por trás, sem disputar a bola, '
                          'dentro da área: pênalti. A Argentina foi campeã nos pênaltis.',
            'cena': cena_campo([76, 14, 108, 66], [
                J('a', 11, (91.6, 52.4), de=(85, 59), ate=(93.4, 51.2), nome='Di María', foco=True, cai=True),
                J('d', 11, (91.2, 53.2), de=(86.5, 61), ate=(92.4, 52.6), nome='Dembélé'),
                J('g', 1, (103.5, 36), de=(103.5, 35), ate=(103.4, 38)),
                J('d', 5, (97, 42), de=(96, 41), ate=(98, 44)),
            ], ((84.5, 59.5), (92, 52.2), (93.5, 50.5)), 'CONTATO', contato=(91.5, 52.8),
                cores={'a': '#7dd3fc', 'd': '#1d4ed8'}),
            'var': {'zoom': {'x': 91.5, 'y': 52.8, 'r': 4}, 'dica': 'Contato por trás que derruba, sem tocar a bola, é falta. Onde foi?'},
        },
        {
            'chave': 'simunic-2006', 'categoria': 'conduta',
            'titulo': 'Copa 2006 · Croácia x Austrália',
            'contexto': 'O zagueiro Josip Šimunić, que já tem um cartão amarelo, comete outra falta merecedora de amarelo '
                        'no meio-campo.',
            'pergunta': 'O que o árbitro deve mostrar?',
            'grupos': [grupo('cartao', 'Cartão', ('nenhum', 'Só advertência verbal'), ('amarelo', 'Amarelo e segue em campo'),
                             ('vermelho', 'Segundo amarelo e vermelho'))],
            'correta': {'cartao': 'vermelho'},
            'explicacao': 'O inglês Graham Poll mostrou o segundo amarelo e esqueceu de expulsar: Šimunić só saiu depois '
                          'do terceiro amarelo. Dois amarelos no mesmo jogo = vermelho.',
            'cena': cena_campo([30, 8, 70, 60], [
                J('a', 9, (49, 30), de=(44, 31), ate=(50.4, 31.4), cai=True),
                J('d', 3, (48.6, 30.7), de=(50, 35), ate=(49.5, 31.5), nome='Šimunić', foco=True),
                J('a', 10, (42, 40), de=(41, 41), ate=(43, 40)),
            ], ((43, 31), (49.2, 30), (50.5, 32)), 'FALTA', contato=(48.9, 30.4),
                cores={'a': '#facc15', 'd': '#dc2626'}),
            'var': {'dica': 'Quantos amarelos ele terá depois deste?'},
        },
        {
            'chave': 'fred-2014', 'categoria': 'area',
            'titulo': 'Abertura da Copa 2014 · Brasil x Croácia',
            'contexto': '1 a 1 em São Paulo. Fred recebe de costas na área, Lovren encosta a mão no ombro dele e Fred vai '
                        'ao chão.',
            'pergunta': 'Qual a marcação?',
            'grupos': [g_marcacao()], 'correta': {'marcacao': 'nada'},
            'explicacao': 'O japonês Yuichi Nishimura deu pênalti e Neymar virou o jogo. Para a maioria dos analistas, o '
                          'contato foi mínimo, insuficiente para derrubar: o certo era seguir o jogo.',
            'cena': cena_campo([78, 12, 108, 58], [
                J('a', 9, (95, 36), de=(91.5, 36), ate=(94.3, 36.8), nome='Fred', foco=True, cai=True),
                J('d', 6, (96.1, 36.1), de=(97.3, 36), ate=(96.3, 36.4), nome='Lovren'),
                J('a', 7, (88, 26), de=(86, 26), ate=(89, 27), nome='Oscar'),
                J('g', 1, (103.5, 34), de=(103.5, 34), ate=(103.5, 34.5)),
            ], ((86, 26.5), (95, 35.8), (95.5, 37.5)), 'CONTATO', contato=(95.5, 36),
                cores={'a': '#facc15', 'd': '#dc2626'}),
            'var': {'zoom': {'x': 95.5, 'y': 36, 'r': 3}, 'dica': 'Contato existe no futebol: ele foi suficiente para derrubar?'},
        },
        {
            'chave': 'wilmots-2002', 'categoria': 'cartao',
            'titulo': 'Copa 2002 · Brasil x Bélgica',
            'contexto': 'Oitavas de final, 0 a 0. Num cruzamento, Wilmots sobe entre os zagueiros brasileiros, há um leve '
                        'contato com Roque Júnior, e ele cabeceia para o gol.',
            'pergunta': 'O gol vale?',
            'grupos': [g_validar()], 'correta': {'decisao': 'gol'},
            'explicacao': 'O jamaicano Peter Prendergast anulou por falta de ataque. As imagens mostram uma disputa normal '
                          'pelo alto: o gol era válido. O Brasil venceu por 2 a 0 e foi pentacampeão.',
            'cena': cena_campo([74, 4, 108, 56], [
                J('a', 7, (98.8, 32), de=(96, 31), ate=(99.5, 32.2), nome='Wilmots', foco=True),
                J('d', 3, (99.2, 33.4), de=(98.5, 35), ate=(99.6, 34.2), nome='Roque Júnior'),
                J('d', 5, (97.5, 29), de=(96.5, 28), ate=(98.4, 29.5)),
                J('g', 1, (103.8, 35.5), de=(103.5, 34), ate=(104.2, 37)),
            ], ((82, 8), (99, 32), (105.6, 36.5)), 'CABECEIO', contato=(99, 32.7),
                cores={'a': '#dc2626', 'd': '#facc15', 'g': '#2563eb'}),
            'var': {'zoom': {'x': 99, 'y': 32.6, 'r': 3}, 'dica': 'Disputa de corpo normal pelo alto não é falta.'},
        },
        {
            'chave': 'kaka-2010', 'categoria': 'conduta',
            'titulo': 'Copa 2010 · Brasil x Costa do Marfim',
            'contexto': 'Kaká, que já tem amarelo, corre para o meio-campo. Keita entra no caminho, o braço de Kaká toca '
                        'levemente o peito dele e Keita cai com as mãos no rosto.',
            'pergunta': 'Qual a decisão correta?',
            'grupos': [grupo('decisao', 'Decisão', ('expulsar_kaka', 'Segundo amarelo e vermelho para Kaká'),
                             ('amarelo_keita', 'Amarelo para Keita por simulação'), ('nada', 'Nada, segue o jogo'))],
            'correta': {'decisao': 'amarelo_keita'},
            'explicacao': 'O francês Stéphane Lannoy expulsou Kaká. O toque foi leve e no peito: Keita simulou uma agressão '
                          'no rosto. Simular para enganar o árbitro é amarelo.',
            'cena': cena_campo([40, 2, 80, 50], [
                J('a', 10, (60, 21), de=(55, 20), ate=(61.5, 21.6), nome='Kaká', foco=True),
                J('d', 19, (60.6, 21.6), de=(62.5, 25), ate=(61.2, 23.2), nome='Keita', cai=True),
                J('a', 5, (52, 30), de=(51, 31), ate=(53, 30)),
            ], ((54, 20), (59.4, 20.8), (63, 20)), 'TOQUE', contato=(60.3, 21.3),
                cores={'a': '#facc15', 'd': '#f97316'}),
            'var': {'zoom': {'x': 60.3, 'y': 21.3, 'r': 3}, 'dica': 'Onde o braço tocou? A reação combina com o contato?'},
        },
    ]


def todos():
    lances = _lances()
    for lance in lances:
        lance['historico'] = True
    return lances

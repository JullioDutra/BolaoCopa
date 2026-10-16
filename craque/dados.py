"""
Dados do "Vida de Craque": clubes, posições, catálogo de efeitos das decisões, cenas e coletivas prontas
(usadas quando a IA está desligada ou falha).
"""

# nome: (força 0-100, cor, liga)
CLUBES = {
    # Brasil
    'Flamengo': (84, '#c8102e', 'Brasileirão'), 'Palmeiras': (84, '#006437', 'Brasileirão'),
    'Atlético-MG': (79, '#111111', 'Brasileirão'), 'Botafogo': (79, '#111111', 'Brasileirão'),
    'São Paulo': (77, '#d00000', 'Brasileirão'), 'Corinthians': (76, '#111111', 'Brasileirão'),
    'Fluminense': (76, '#7a0026', 'Brasileirão'), 'Grêmio': (75, '#0d80bf', 'Brasileirão'),
    'Internacional': (76, '#e30613', 'Brasileirão'), 'Cruzeiro': (76, '#0033a0', 'Brasileirão'),
    'Bahia': (73, '#0047ab', 'Brasileirão'), 'Fortaleza': (72, '#0c3e8c', 'Brasileirão'),
    'Vasco': (72, '#111111', 'Brasileirão'), 'Santos': (71, '#111111', 'Brasileirão'),
    'Athletico-PR': (71, '#c8102e', 'Brasileirão'), 'Vitória': (66, '#e30613', 'Brasileirão'),
    'Sport': (65, '#c8102e', 'Brasileirão'), 'Ceará': (65, '#111111', 'Brasileirão'),
    'Juventude': (63, '#0f7a3a', 'Brasileirão'), 'Mirassol': (64, '#f2c500', 'Brasileirão'),
    # Europa
    'Real Madrid': (93, '#f5f5f5', 'Europa'), 'Barcelona': (91, '#a50044', 'Europa'),
    'Manchester City': (92, '#6cabdd', 'Europa'), 'Liverpool': (90, '#c8102e', 'Europa'),
    'Arsenal': (89, '#ef0107', 'Europa'), 'Bayern de Munique': (91, '#dc052d', 'Europa'),
    'PSG': (90, '#004170', 'Europa'), 'Inter de Milão': (87, '#0068a8', 'Europa'),
    'Milan': (84, '#fb090b', 'Europa'), 'Juventus': (84, '#111111', 'Europa'),
    'Atlético de Madrid': (85, '#cb3524', 'Europa'), 'Chelsea': (86, '#034694', 'Europa'),
    'Benfica': (80, '#e30613', 'Europa'), 'Porto': (80, '#00428c', 'Europa'),
    'Ajax': (78, '#d2122e', 'Europa'), 'Sevilla': (78, '#d4021d', 'Europa'),
    'Napoli': (85, '#12a0d7', 'Europa'), 'Borussia Dortmund': (85, '#fde100', 'Europa'),
}
CLUBES_INICIAIS = ['Santos', 'Vasco', 'Bahia', 'Fortaleza', 'Athletico-PR', 'Grêmio', 'Cruzeiro', 'Fluminense',
                   'São Paulo', 'Corinthians', 'Internacional', 'Botafogo', 'Atlético-MG', 'Palmeiras', 'Flamengo']

POSICOES = {
    # posição: (peso técnica, peso físico, peso mental, gols esperados por 90', assistências por 90')
    'Atacante': (0.45, 0.35, 0.20, 0.55, 0.18),
    'Meia': (0.50, 0.20, 0.30, 0.22, 0.32),
    'Volante': (0.35, 0.35, 0.30, 0.08, 0.12),
    'Lateral': (0.35, 0.45, 0.20, 0.06, 0.18),
    'Zagueiro': (0.25, 0.45, 0.30, 0.06, 0.03),
}

RODADAS_POR_TEMPORADA = 10
COLETIVA_NAS_RODADAS = (2, 5, 8)        # índices (0..9): depois desses jogos tem coletiva
MAX_TEMPORADAS = 8
IDADE_INICIAL = 17

# efeitos das decisões: a IA escolhe um destes nomes; os números são sempre do servidor
EFEITOS = {
    'treino': {'tecnica': 2, 'fisico': 1, 'forma': 4, 'moral': -1},
    'descanso': {'forma': 7, 'tecnico': -1},
    'balada': {'moral': 5, 'forma': -9, 'tecnico': -6, 'torcida': -3, 'fama': 2},
    'midia': {'fama': 6, 'tecnico': -2, 'moral': 1},
    'familia': {'moral': 7, 'mental': 1},
    'tecnico': {'tecnico': 8, 'moral': 1},
    'confronto': {'tecnico': -9, 'moral': 3, 'fama': 3, 'torcida': 2},
    'torcida': {'torcida': 8, 'fama': 2},
    'caridade': {'torcida': 5, 'fama': 3, 'moral': 3},
    'sacrificio': {'forma': -8, 'torcida': 6, 'tecnico': 5},
    'estudo': {'mental': 2, 'tecnica': 1},
    'empresario': {'fama': 4, 'moral': -2, 'tecnico': -2},
    'polemica': {'fama': 5, 'torcida': -7, 'tecnico': -3},
    'neutro': {},
}
ROTULOS = {'tecnica': 'Técnica', 'fisico': 'Físico', 'mental': 'Mental', 'forma': 'Forma', 'moral': 'Moral',
           'fama': 'Fama', 'torcida': 'Torcida', 'tecnico': 'Técnico'}

# tom da resposta na coletiva -> efeitos
TONS = {
    'humilde': {'tecnico': 4, 'torcida': 3, 'fama': 1},
    'confiante': {'fama': 4, 'moral': 3, 'torcida': 2},
    'provocador': {'fama': 7, 'torcida': 4, 'tecnico': -5},
    'evasivo': {'fama': -2, 'tecnico': 1},
    'emocionado': {'torcida': 6, 'moral': 2, 'fama': 2},
    'polemico': {'fama': 8, 'tecnico': -8, 'torcida': -4, 'moral': -2},
}
ROTULO_TOM = {'humilde': 'Humilde', 'confiante': 'Confiante', 'provocador': 'Provocador', 'evasivo': 'Evasivo',
              'emocionado': 'Emocionado', 'polemico': 'Polêmico'}

CENAS = [
    ('Véspera de clássico. Os veteranos do elenco chamam você para uma festa "rapidinha" na casa de um deles.',
     [('Vou, mas volto cedo', 'balada'), ('Fico em casa vendo vídeo dos adversários', 'estudo'), ('Durmo cedo, amanhã é guerra', 'descanso')]),
    ('O técnico quer que você treine numa posição diferente, mais recuada, por algumas semanas.',
     [('Aceito sem reclamar', 'tecnico'), ('Peço uma conversa e defendo minha posição', 'confronto'), ('Treino dobrado para provar meu valor', 'treino')]),
    ('Um empresário famoso liga oferecendo "abrir portas na Europa" se você assinar com ele hoje.',
     [('Assino na hora', 'empresario'), ('Converso com a família antes', 'familia'), ('Recuso: foco no clube', 'tecnico')]),
    ('Um vídeo seu fazendo embaixadinha viralizou nas redes. Uma marca quer gravar um comercial.',
     [('Gravo o comercial', 'midia'), ('Gravo, mas só na folga', 'torcida'), ('Recuso, agora é só futebol', 'treino')]),
    ('Você sente um incômodo na coxa no aquecimento do treino. O departamento médico sugere poupar.',
     [('Peço para ser poupado', 'descanso'), ('Jogo no sacrifício', 'sacrificio'), ('Faço fisioterapia extra à noite', 'treino')]),
    ('A torcida organizada protesta no CT depois de duas derrotas e quer conversar com os jogadores.',
     [('Vou até eles e assumo a responsabilidade', 'torcida'), ('Fico quieto, deixo os capitães falarem', 'neutro'), ('Respondo nas redes que torcedor não ganha jogo', 'polemica')]),
    ('Um hospital infantil da cidade convida o elenco para uma visita no dia de folga.',
     [('Vou e levo camisas autografadas', 'caridade'), ('Mando um vídeo de apoio', 'midia'), ('Aproveito a folga com a família', 'familia')]),
    ('O técnico critica sua marcação na frente de todo o elenco no vestiário.',
     [('Peço desculpas e prometo melhorar', 'tecnico'), ('Rebato na hora', 'confronto'), ('Fico calado e treino mais', 'treino')]),
    ('Sua mãe liga dizendo que sente sua falta e que você está diferente desde que virou profissional.',
     [('Viajo para vê-la na folga', 'familia'), ('Prometo ligar mais vezes', 'neutro'), ('Digo que agora não dá, é o sonho', 'treino')]),
    ('Um ídolo do clube, já aposentado, se oferece para treinar finalização com você depois dos treinos.',
     [('Aceito e fico até escurecer', 'treino'), ('Peço dicas de como lidar com a pressão', 'estudo'), ('Agradeço, mas preciso descansar', 'descanso')]),
    ('Um jornalista pede uma entrevista exclusiva sobre o seu futuro e os boatos de transferência.',
     [('Dou a entrevista e falo do sonho europeu', 'empresario'), ('Falo só do clube atual', 'torcida'), ('Recuso educadamente', 'neutro')]),
    ('O capitão do time pede que você assuma as cobranças de pênalti no próximo jogo.',
     [('Aceito o desafio', 'torcida'), ('Treino pênaltis a semana toda antes', 'treino'), ('Prefiro deixar com quem já bate', 'tecnico')]),
]

COLETIVAS = [
    ('Rafaela Monteiro', 'Rádio Arquibancada', 'A torcida já canta seu nome. Você se sente pronto para ser o protagonista do time?'),
    ('Jorge Bastos', 'Jornal do Gramado', 'Falam que você está pensando mais na Europa do que no clube. O que responde?'),
    ('Camila Torres', 'Canal Resenha FC', 'O técnico tem te deixado no banco em alguns jogos. Isso te incomoda?'),
    ('Marcos Vidal', 'Portal Bola Rolando', 'Qual foi o momento mais difícil da sua carreira até aqui e como você superou?'),
    ('Luiza Prado', 'TV Placar', 'O rival da próxima rodada disse que você é superestimado. Algum recado para ele?'),
    ('André Lins', 'Rádio Bola Cheia', 'O que você mudou na rotina para chegar nesse nível de atuação?'),
]
# respostas prontas quando não há IA: (texto do botão, tom, qualidade 0-10)
RESPOSTAS_PRONTAS = [
    ('Agradecer o grupo e o técnico, sem se colocar acima de ninguém', 'humilde', 7),
    ('Dizer que está pronto e que os gols vão continuar saindo', 'confiante', 7),
    ('Mandar um recado afiado para os críticos', 'provocador', 6),
    ('Desconversar e dizer que só pensa no próximo jogo', 'evasivo', 4),
]

PREMIOS = {
    'craque': 'Craque da Temporada', 'artilheiro': 'Artilheiro', 'garcom': 'Garçom (rei das assistências)',
    'revelacao': 'Revelação', 'campeao': 'Campeão',
}

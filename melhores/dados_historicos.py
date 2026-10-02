"""
Histórico das votações "Melhores do Ano" do grupo — base das odds.

Fontes:
  * 2025: 26 respostas do formulário "Os Melhores do Ano 2025 – Cartolândia"
          (apenas contagens agregadas, sem identificar quem votou em quem).
  * 2021: 30 respostas do "Troféu Cartolândia 2021" (só categorias equivalentes
          e só quem ainda está no grupo).

Formato de cada categoria:
    (slug, nome, emoji, tipo, descrição, {candidato: (votos_2025, votos_2021)})

Tipos:
    pessoa -> o candidato é o próprio cartoleiro
    autor  -> categoria de "frases/lances" (pérola, mico, jantada...). Na bet o
              candidato é QUEM vai protagonizar; as odds usam quantas vezes cada
              um foi o autor das frases mais votadas no passado.
    nome   -> nomes do grupo/chat
"""

CATEGORIAS = [
    ('cartoleiro', 'Cartoleiro do Ano', '🎩', 'pessoa',
     'Quem mais mitou no Cartola e na resenha ao longo do ano.',
     {'Adilson': (12, 1), 'Marcos Vinicius': (6, 0), 'Mark': (4, 0), 'Marcos Fabio': (2, 0),
      'Yuri Martins': (1, 0), 'Matheus Santiago': (1, 0), 'Filipe': (0, 3)}),

    ('nunca-critiquei', 'Nunca Critiquei (mais sensato)', '🕊️', 'pessoa',
     'O mais sensato do grupo: o homi que nunca criticou ninguém.',
     {'Gabriel': (14, 0), 'Lucas Rafael': (7, 0), 'Fabio Junio': (4, 3), 'Lucas Junior': (1, 0),
      'Jullio': (0, 5), 'Pedro': (0, 5)}),

    ('rei-das-fakes', 'Rei das Fakes', '🃏', 'pessoa',
     'Dono das notícias mais "confiáveis" e dos prints mais criativos.',
     {'William Cardoso': (17, 22), 'Arthur Rocha': (3, 0), 'Marcos Vinicius': (3, 0),
      'Matheus Santiago': (2, 0), 'Yuri Martins': (1, 0), 'Lucas Junior': (0, 4),
      'Adilson': (0, 3), 'Filipe': (0, 1)}),

    ('dinizismo', 'Dinizismo (sem argumentos)', '🗣️', 'pessoa',
     'Defende o indefensável sem um único argumento.',
     {'William Cardoso': (9, 4), 'Arthur Rocha': (9, 14), 'Mark': (4, 0), 'João Pires': (3, 0),
      'Elves Nunes': (1, 5), 'Filipe': (0, 0), 'Jullio': (0, 0)}),

    ('sormani', 'Prêmio Sormani (quem não entende de futebol)', '🤷', 'pessoa',
     'Opinião de futebol? Melhor nem perguntar.',
     {'Arthur Rocha': (9, 0), 'William Cardoso': (5, 0), 'Mark': (4, 0), 'Paulo Victor': (2, 0),
      'Matheus Santiago': (2, 0), 'Yuri Martins': (2, 0), 'Jullio': (1, 0), 'Marcos Vinicius': (1, 0)}),

    ('nuvem', 'Prêmio Nuvem (Clubista do Ano)', '☁️', 'pessoa',
     'O clubista mais fanático: só enxerga o próprio time.',
     {'Arthur Rocha': (8, 2), 'Paulo Victor': (7, 7), 'Yuri Martins': (4, 0), 'William Cardoso': (3, 9),
      'Matheus Santiago': (2, 8), 'Andre Borghi': (2, 0), 'Marcos Vinicius': (0, 4)}),

    ('augusto-melo', 'Prêmio Augusto Melo (Caloteiro)', '💵', 'pessoa',
     'Quem mais deixou a resenha (e o bolão) no vermelho.',
     {'Matheus Santiago': (15, 6), 'Mark': (7, 0), 'Adilson': (2, 0), 'Rubyan': (2, 0),
      'João Pires': (0, 0), 'Elves Nunes': (0, 25), 'William Cardoso': (0, 4)}),

    ('nome-grupo', 'Melhor Nome do Grupo', '🏷️', 'nome',
     'O nome de grupo que mais representou a Cartolândia.',
     {'SAFANOVLANDIA': (16, 0), 'MUSHUC RUNANLANDIA': (5, 0), 'NEYMARLANDIA': (3, 0),
      'LANUSLANDIA': (2, 0), 'CRBLANDIA': (0, 0), 'DINIZLANDIA': (0, 0), 'KJLANDIA': (0, 0)}),

    ('vagabundo', 'Vagabundo do Ano', '🛋️', 'pessoa',
     'Sumiu, deu migué ou enrolou — o campeão da vagabundagem.',
     {'Matheus Santiago': (12, 0), 'Mark': (7, 0), 'Paulo Victor': (7, 0),
      'Lucas Junior': (0, 0), 'Adilson': (0, 0)}),

    ('perola', 'Pérola do Ano', '💎', 'autor',
     'Quem vai soltar a frase mais lendária de 2026.',
     {'Arthur Rocha': (14, 0), 'Paulo Victor': (4, 0), 'William Cardoso': (3, 0), 'Andre Borghi': (2, 0),
      'Geovani Marconi': (2, 0), 'Marcos Vinicius': (1, 0), 'João Pires': (0, 0)}),

    ('mico', 'Mico do Ano', '🐒', 'autor',
     'Quem vai pagar o maior mico: previsão que envelhece mal.',
     {'Arthur Rocha': (11, 1), 'Matheus Santiago': (11, 10), 'Paulo Victor': (3, 0),
      'William Cardoso': (1, 5), 'Marcos Vinicius': (0, 6)}),

    ('fala-bosta', 'Fala Bosta do Ano', '💩', 'pessoa',
     'Fala muito e acerta pouco.',
     {'William Cardoso': (10, 12), 'Arthur Rocha': (8, 2), 'Paulo Victor': (3, 0), 'Mark': (3, 0),
      'Matheus Santiago': (2, 9), 'Marcos Vinicius': (0, 0), 'João Pires': (0, 0), 'Rony Cardoso': (0, 0)}),

    ('aloprador', 'Aloprador do Ano (quem mais encheu o saco)', '📢', 'pessoa',
     'Spam, áudio longo e marcação em tudo: quem mais encheu o saco.',
     {'Mark': (15, 0), 'Arthur Rocha': (3, 0), 'Paulo Victor': (3, 0), 'Marcos Vinicius': (3, 0),
      'João Pires': (1, 0), 'William Cardoso': (1, 0), 'Matheus Santiago': (0, 0)}),

    ('jantada', 'Jantada do Ano', '🍽️', 'autor',
     'Quem vai dar (ou levar) a maior jantada nas discussões.',
     {'William Cardoso': (10, 0), 'Matheus Santiago': (6, 0), 'Pedro': (4, 0), 'Mark': (4, 0),
      'Paulo Victor': (2, 0)}),

    ('rei-das-tretas', 'Rei das Tretas', '🔥', 'pessoa',
     'Onde tem confusão, ele está no meio.',
     {'Paulo Victor': (18, 16), 'Matheus Santiago': (5, 0), 'Pedro': (2, 0), 'João Pires': (1, 0),
      'Marcos Fabio': (0, 0), 'Rony Cardoso': (0, 0), 'Marcos Vinicius': (0, 10)}),

    ('vergonha', 'Vergonha do Ano', '🫣', 'autor',
     'Quem vai protagonizar a maior vergonha alheia.',
     {'Arthur Rocha': (8, 2), 'Matheus Santiago': (6, 0), 'Yuri Martins': (5, 0), 'João Pires': (3, 0),
      'Marcos Vinicius': (2, 13), 'Andre Borghi': (1, 0), 'William Cardoso': (1, 4)}),

    ('zicador', 'Zicador do Ano', '🐈‍⬛', 'autor',
     'Falou, apostou e o time dele dançou.',
     {'Matheus Santiago': (20, 0), 'Andre Borghi': (2, 0), 'Diogo Henrique': (2, 0), 'Paulo Victor': (2, 0)}),

    ('pau-mole', 'Pau Mole do Ano', '🥀', 'autor',
     'Amarelou, sumiu na derrota ou não sustentou o favoritismo.',
     {'William Cardoso': (14, 0), 'Paulo Victor': (4, 0), 'Mark': (4, 0), 'Diogo Henrique': (4, 0),
      'Yuri Martins': (3, 0), 'Rony Cardoso': (1, 0), 'Gabriel': (1, 0)}),

    ('mais-chato', 'Mais Chato do Ano', '😤', 'pessoa',
     'O mais chato do grupo — com todo carinho.',
     {'Mark': (16, 0), 'Paulo Victor': (7, 0), 'William Cardoso': (3, 0), 'Rony Cardoso': (0, 0),
      'João Pires': (0, 0)}),

    ('iludido', 'Iludido do Ano', '🤡', 'autor',
     'Quem vai se iludir com o próprio time (e se dar mal).',
     {'William Cardoso': (10, 10), 'Arthur Rocha': (8, 1), 'Matheus Santiago': (5, 0),
      'Marcos Fabio': (2, 0), 'Mark': (1, 0), 'Diogo Henrique': (1, 0), 'Marcos Vinicius': (0, 13)}),

    ('passa-pano', 'Passa Pano', '🧽', 'autor',
     'Quem vai passar pano pro jogador (ou time) mais indefensável.',
     {'Arthur Rocha': (11, 0), 'Paulo Victor': (8, 10), 'João Pires': (5, 0), 'Marcos Fabio': (1, 0),
      'Jullio': (1, 0), 'Elves Nunes': (0, 6), 'Yuri Martins': (0, 2)}),

    ('la-ele', 'Lá Ele', '🫵', 'autor',
     'Quem vai protagonizar o "lá ele" do ano.',
     {'Paulo Victor': (10, 0), 'Thiagos Enes': (8, 0), 'Lucas Junior': (5, 0), 'Marcos Fabio': (3, 0)}),
]

TOTAL_RESPOSTAS_2025 = 26
TOTAL_RESPOSTAS_2021 = 30


# ---------------------------------------------------------------------------
# Participantes (quem respondeu os formulários), com o nome já padronizado.
# Entram como candidatos em todas as categorias de pessoa/autor; quem nunca
# foi votado ali fica com odd alta (azarão), pois só tem a "suavização" de peso.
# ---------------------------------------------------------------------------
PARTICIPANTES_2025 = [
    'João Pires', 'Adilson', 'Diogo Henrique', 'Mark', 'Arthur Gabriel', 'Pedro', 'Yuri Martins',
    'Paulo Victor', 'Gabriel', 'Fabio Junio', 'Elves Nunes', 'William Cardoso', 'Henrique',
    'Marcos Vinicius', 'Geovani Marconi', 'Lucas Junior', 'Rony Cardoso', 'Rubyan', 'Andre Borghi',
    'Matheus Santiago', 'Filipe', 'Anderson', 'Jullio', 'Marcos Fabio', 'Lucas Rafael',
    'Arthur Rocha', 'Thiagos Enes',
]

# Responderam só o Troféu 2021 (não aparecem em 2025). Só entram com --incluir-2021.
PARTICIPANTES_SO_2021 = [
    'Maycon', 'Alexssandro', 'Lari', 'Pedrin', 'Luizzz', 'Lulu', 'Dantas', 'Heloísa', 'Heyder',
    'João Beiramar', 'Tati', 'Fael Mitinho', 'Bruno',
]

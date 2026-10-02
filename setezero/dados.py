"""
Times históricos do "7 a 0". Elencos e notas (0–99) são APROXIMAÇÕES inspiradas na memória do torcedor,
não dados oficiais — o objetivo é a resenha. Formato do elenco: "Nome,POS,nota;..." com
POS = GOL ZAG LAT VOL MEI PON ATA. Os 11 primeiros formam o time-base; o resto é banco.
"""
import zlib

# chave, clube (para o escudo global), ano, apelido, cor, formação-base, técnico, elenco
_TIMES = [
    ('fla-1981', 'Flamengo', 1981, 'O Mundial de Zico', '#c8102e', '4-3-3', 'Paulo César Carpegiani',
     'Raul,GOL,80;Leandro,LAT,85;Marinho,ZAG,80;Mozer,ZAG,82;Júnior,LAT,88;Andrade,VOL,82;Adílio,MEI,84;Zico,MEI,97;'
     'Tita,ATA,82;Nunes,ATA,84;Lico,PON,80;Cantarele,GOL,72;Figueiredo,ZAG,74;Peu,ATA,75;Anselmo,MEI,74'),
    ('fla-2019', 'Flamengo', 2019, 'A Máquina de Jesus', '#c8102e', '4-3-3', 'Jorge Jesus',
     'Diego Alves,GOL,83;Rafinha,LAT,82;Rodrigo Caio,ZAG,82;Pablo Marí,ZAG,80;Filipe Luís,LAT,86;Willian Arão,VOL,80;'
     'Gerson,MEI,86;Éverton Ribeiro,MEI,85;Arrascaeta,MEI,88;Bruno Henrique,ATA,90;Gabigol,ATA,91;'
     'César,GOL,70;Diego,MEI,80;Vitinho,PON,76;Thuler,ZAG,74'),
    ('cor-1999', 'Corinthians', 1999, 'O Time do Marcelinho', '#1a1a1a', '4-4-2', 'Oswaldo de Oliveira',
     'Dida,GOL,86;Índio,ZAG,76;Adílson,ZAG,76;Fábio Luciano,ZAG,77;Kléber,LAT,76;Vampeta,VOL,82;Rincón,VOL,84;'
     'Ricardinho,MEI,82;Marcelinho Carioca,MEI,88;Edilson,ATA,85;Luizão,ATA,84;Gilberto,LAT,75;Dinei,ATA,78;Fernando,GOL,70;Silvinho,LAT,74'),
    ('cor-2012', 'Corinthians', 2012, 'O Invicto do Mundial', '#1a1a1a', '4-2-3-1', 'Tite',
     'Cássio,GOL,83;Alessandro,LAT,77;Chicão,ZAG,78;Paulo André,ZAG,78;Fábio Santos,LAT,79;Ralf,VOL,82;Paulinho,VOL,84;'
     'Danilo,MEI,83;Emerson Sheik,PON,79;Jorge Henrique,PON,76;Guerrero,ATA,86;Romarinho,ATA,76;Liédson,ATA,77;Welder,GOL,68;Edenílson,MEI,72'),
    ('pal-1999', 'Palmeiras', 1999, 'A Libertadores de Felipão', '#006437', '4-4-2', 'Luiz Felipe Scolari',
     'Marcos,GOL,90;Arce,LAT,82;Roque Júnior,ZAG,82;Júnior Baiano,ZAG,80;Júnior,LAT,78;César Sampaio,VOL,82;'
     'Flávio Conceição,VOL,80;Alex,MEI,90;Zinho,MEI,84;Paulo Nunes,ATA,82;Evair,ATA,84;Euller,ATA,80;Galeano,ZAG,74;Magrão,MEI,72;Sérgio,GOL,68'),
    ('pal-2021', 'Palmeiras', 2021, 'O Bicampeão da América', '#006437', '4-3-3', 'Abel Ferreira',
     'Weverton,GOL,85;Mayke,LAT,80;Gustavo Gómez,ZAG,87;Luan,ZAG,78;Piquerez,LAT,80;Danilo,VOL,81;Zé Rafael,MEI,80;'
     'Raphael Veiga,MEI,86;Rony,PON,83;Dudu,PON,84;Luiz Adriano,ATA,80;Breno Lopes,ATA,76;Gabriel Menino,LAT,76;Atuesta,VOL,76;Jailson,GOL,68'),
    ('spa-2006', 'São Paulo', 2006, 'O Tri do Ceni', '#e30613', '4-4-2', 'Muricy Ramalho',
     'Rogério Ceni,GOL,91;Cicinho,LAT,80;Fabão,ZAG,78;Lugano,ZAG,85;Júnior,LAT,78;Josué,VOL,80;Mineiro,VOL,80;'
     'Danilo,MEI,84;Souza,MEI,80;Aloísio,ATA,78;Amoroso,ATA,82;Borges,ATA,82;Alex Silva,ZAG,74;Richarlyson,VOL,76;Bosco,GOL,68'),
    ('san-1962', 'Santos', 1962, 'O Santos do Rei', '#1a1a1a', '4-3-3', 'Lula',
     'Gilmar,GOL,90;Lima,LAT,78;Mauro,ZAG,83;Calvet,ZAG,78;Dalmo,LAT,80;Zito,VOL,86;Mengálvio,MEI,84;Coutinho,ATA,89;'
     'Pelé,ATA,99;Pepe,PON,88;Dorval,PON,82;Laércio,GOL,70;Ismael,ZAG,72;Pagão,ATA,80;Formiga,VOL,76'),
    ('san-2002', 'Santos', 2002, 'Os Meninos da Vila', '#1a1a1a', '4-2-3-1', 'Emerson Leão',
     'Fábio Costa,GOL,81;Maurinho,LAT,75;Alex,ZAG,78;Preto Casagrande,ZAG,75;Leonardo,LAT,73;Paulo Almeida,VOL,78;'
     'Renato,VOL,80;Elano,MEI,83;Diego,MEI,88;Robinho,PON,91;Alberto,ATA,80;Deivid,ATA,78;Michel,PON,72;Léo,LAT,72;Zetti,GOL,70'),
    ('cru-2003', 'Cruzeiro', 2003, 'A Tríplice Coroa', '#0033a0', '4-4-2', 'Vanderlei Luxemburgo',
     'Gomes,GOL,80;Maurinho,LAT,76;Luisão,ZAG,83;Cris,ZAG,84;Leandro,LAT,75;Augusto Recife,VOL,78;Maldonado,VOL,79;'
     'Wendell,MEI,80;Alex,MEI,93;Aristizábal,ATA,85;Deivid,ATA,84;Mota,ATA,76;Fábio,GOL,68;Edu Dracena,ZAG,76;Jussiê,MEI,72'),
    ('cam-2021', 'Atlético-MG', 2021, 'O Galo Dobradinha', '#1a1a1a', '4-2-3-1', 'Cuca',
     'Everson,GOL,83;Mariano,LAT,78;Nathan Silva,ZAG,76;Junior Alonso,ZAG,81;Guilherme Arana,LAT,85;Allan,VOL,82;Jair,VOL,78;'
     'Nacho Fernández,MEI,83;Hulk,ATA,91;Zaracho,PON,77;Keno,PON,81;Diego Costa,ATA,82;Savarino,PON,78;Réver,ZAG,75;Cleiton,GOL,68'),
    ('gre-2017', 'Grêmio', 2017, 'A Imortal de Renato', '#0d80bf', '4-3-3', 'Renato Gaúcho',
     'Grohe,GOL,83;Edílson,LAT,77;Geromel,ZAG,85;Kannemann,ZAG,82;Bruno Cortez,LAT,76;Michel,VOL,80;Arthur,MEI,86;'
     'Ramiro,MEI,79;Luan,MEI,88;Fernandinho,PON,80;Lucas Barrios,ATA,81;Everton,PON,83;Jael,ATA,75;Léo Moura,LAT,76;Marcelo Oliveira,GOL,66'),
    ('int-2006', 'Internacional', 2006, 'O Mundial Colorado', '#e5050f', '4-4-2', 'Abel Braga',
     'Clemer,GOL,79;Ceará,LAT,77;Índio,ZAG,81;Fabiano Eller,ZAG,78;Rubens Cardoso,LAT,75;Edinho,VOL,78;'
     'Wellington Monteiro,VOL,77;Fernandão,MEI,88;Alex,MEI,85;Rafael Sóbis,ATA,84;Iarley,ATA,82;Pato,ATA,80;Tinga,VOL,78;Danny Morais,ZAG,72;Renan,GOL,66'),
    ('flu-2012', 'Fluminense', 2012, 'O Tetra do Fred', '#9f0e2f', '4-4-2', 'Abel Braga',
     'Diego Cavalieri,GOL,81;Bruno,LAT,75;Gum,ZAG,78;Leandro Euzébio,ZAG,76;Carlinhos,LAT,73;Edinho,VOL,78;Jean,VOL,76;'
     'Thiago Neves,MEI,86;Deco,MEI,84;Fred,ATA,87;Wellington Nem,PON,82;Rafael Sóbis,ATA,80;Digão,ZAG,72;Valência,PON,76;Berna,GOL,64'),
    ('bot-2024', 'Botafogo', 2024, 'O Glorioso Campeão da América', '#1a1a1a', '4-3-3', 'Artur Jorge',
     'John,GOL,78;Vitinho,LAT,79;Bastos,ZAG,81;Adryelson,ZAG,78;Cuiabano,LAT,76;Gregore,VOL,81;Marlon Freitas,MEI,80;'
     'Almada,MEI,85;Savarino,PON,82;Luiz Henrique,PON,86;Júnior Santos,ATA,82;Tiquinho Soares,ATA,83;Alexander Barboza,ZAG,79;Eduardo,VOL,76;Gatito Fernández,GOL,72'),
    ('vas-1997', 'Vasco', 1997, 'O Vasco do Animal', '#1a1a1a', '4-4-2', 'Antônio Lopes',
     'Carlos Germano,GOL,81;Vágner,LAT,74;Odvan,ZAG,76;Mauro Galvão,ZAG,81;Felipe,LAT,77;Nasa,VOL,76;Ramon,VOL,78;'
     'Juninho Pernambucano,MEI,87;Luizão,ATA,81;Edmundo,ATA,92;Donizete,ATA,80;Válber,MEI,74;Pedrinho,MEI,76;Gilberto,LAT,72;Hélton,GOL,66'),
    ('sao-1993', 'São Paulo', 1993, 'O Bi Mundial de Telê', '#e30613', '4-3-3', 'Telê Santana',
     'Zetti,GOL,84;Vítor,LAT,77;Ronaldão,ZAG,80;Válber,ZAG,76;Leonardo,LAT,81;Doriva,VOL,76;Palhinha,MEI,83;'
     'Raí,MEI,92;Müller,PON,84;Cafu,LAT,85;Elivélton,PON,80;Muller,ATA,82;Macedo,ZAG,72;Cerezo,MEI,78;Gilmar,GOL,66'),
]

# Adversários fictícios do "Desafio 7 a 0" — fracos de propósito
_FREGUESES = [
    ('varzea-fc', 'Várzea F.C.', 0, 'Os Pernas de Pau do Bairro', '#6b7280', '4-4-2', 'Seu Zé da Padaria',
     'Marreco,GOL,69;Tiãozinho,LAT,67;Caneta,ZAG,69;Bigode,ZAG,68;Neguinho,LAT,66;Pelanca,VOL,69;Gordinho,VOL,67;'
     'Juninho do Posto,MEI,70;Zé Pequeno,MEI,68;Matador,ATA,71;Pixote,ATA,67;Reserva 1,GOL,57;Reserva 2,ZAG,59;Reserva 3,MEI,60;Reserva 4,ATA,61'),
    ('tiozao-fc', 'Tiozão United', 0, 'A Pelada dos 40+', '#9ca3af', '4-3-3', 'Dr. Barriga',
     'Seu Chico,GOL,67;Carlão,LAT,65;Dentuço,ZAG,67;Chorão,ZAG,66;Magrelo,LAT,64;Careca,VOL,68;Paulão,MEI,69;'
     'Dindinho,MEI,67;Canhoto,PON,70;Fominha,ATA,69;Alemão,PON,67;Banco 1,GOL,57;Banco 2,ZAG,58;Banco 3,MEI,59;Banco 4,ATA,60'),
    ('sub15', 'Sub-15 do Colégio', 0, 'Os Pivetes', '#a3a3a3', '4-4-2', 'Prof. Carlos (Ed. Física)',
     'Lucas,GOL,71;Davi,LAT,69;Miguel,ZAG,70;Arthur,ZAG,69;Heitor,LAT,68;Gabriel,VOL,71;Bernardo,VOL,69;'
     'Samuel,MEI,72;Pedro,MEI,70;Enzo,ATA,73;Nicolas,ATA,69;Re 1,GOL,57;Re 2,ZAG,59;Re 3,MEI,60;Re 4,ATA,62'),
]

# Peso de cada posição no "estilo" do jogador: (ataque, criação, defesa, goleiro)
_PERFIL = {
    'GOL': (-60, -50, -35, 0),
    'ZAG': (-42, -20, 0, -60),
    'LAT': (-16, -10, -7, -60),
    'VOL': (-26, -5, -3, -60),
    'MEI': (-8, 0, -24, -60),
    'PON': (-3, -8, -36, -60),
    'ATA': (0, -20, -46, -60),
}

FORMACOES = {
    '4-3-3': ['GOL', 'LAT', 'ZAG', 'ZAG', 'LAT', 'VOL', 'MEI', 'MEI', 'PON', 'ATA', 'PON'],
    '4-4-2': ['GOL', 'LAT', 'ZAG', 'ZAG', 'LAT', 'VOL', 'VOL', 'MEI', 'MEI', 'ATA', 'ATA'],
    '3-5-2': ['GOL', 'ZAG', 'ZAG', 'ZAG', 'LAT', 'VOL', 'VOL', 'MEI', 'LAT', 'ATA', 'ATA'],
    '4-2-3-1': ['GOL', 'LAT', 'ZAG', 'ZAG', 'LAT', 'VOL', 'VOL', 'PON', 'MEI', 'PON', 'ATA'],
}

# custo (pontos de nota) de escalar alguém fora da posição natural
_AFINIDADE = {
    ('ATA', 'PON'): 3, ('PON', 'ATA'): 3, ('MEI', 'VOL'): 5, ('VOL', 'MEI'): 5, ('MEI', 'PON'): 4, ('PON', 'MEI'): 4,
    ('LAT', 'ZAG'): 7, ('ZAG', 'LAT'): 7, ('LAT', 'VOL'): 6, ('VOL', 'LAT'): 6, ('VOL', 'ZAG'): 8, ('ZAG', 'VOL'): 8,
    ('LAT', 'PON'): 8, ('PON', 'LAT'): 8, ('MEI', 'ATA'): 8, ('ATA', 'MEI'): 8,
}


def custo_posicao(natural, slot):
    if natural == slot:
        return 0
    if 'GOL' in (natural, slot):
        return 60
    return _AFINIDADE.get((natural, slot), 20)


def _jogador(nome, pos, nota):
    base = zlib.crc32(nome.encode())
    atq, cri, dfs, gol = (max(10, min(99, nota + d)) for d in _PERFIL[pos])
    finalizacao = max(10, min(99, atq + ((base % 9) - 4)))
    return {'nome': nome, 'pos': pos, 'nota': nota, 'atq': atq, 'cri': cri, 'def': dfs, 'gol': gol, 'fin': finalizacao}


def _montar(chave, clube, ano, apelido, cor, formacao, tecnico, elenco):
    jogadores = []
    for item in elenco.split(';'):
        nome, pos, nota = item.rsplit(',', 2)
        jogadores.append(_jogador(nome.strip(), pos.strip(), int(nota)))
    forca = forcas(escalar({'elenco': jogadores}, formacao))
    return {'chave': chave, 'clube': clube, 'ano': ano, 'nome': f'{clube} {ano}', 'apelido': apelido, 'cor': cor,
            'formacao': formacao, 'tecnico': tecnico, 'elenco': jogadores, 'forca': forca,
            'overall': round((forca['atq'] + forca['cri'] + forca['def'] + forca['gol']) / 4)}


def forcas(xi):
    """ Força por setor do time em campo (lista de jogadores): ataque, meio (criação), defesa e goleiro. """
    def media(itens, campo, pesos=None):
        if not itens:
            return 30.0
        pesos = pesos or [1.0] * len(itens)
        return sum(j[campo] * w for j, w in zip(itens, pesos)) / sum(pesos)

    ata = [j for j in xi if j['pos'] in ('ATA', 'PON')]
    mei = [j for j in xi if j['pos'] in ('MEI', 'VOL')]
    dfs = [j for j in xi if j['pos'] in ('ZAG', 'LAT', 'VOL')]
    pesos_def = [1.0 if j['pos'] == 'ZAG' else 0.8 if j['pos'] == 'LAT' else 0.6 for j in dfs]
    gol = [j for j in xi if j['pos'] == 'GOL']
    return {
        'atq': round(0.8 * media(ata, 'atq') + 0.2 * media(mei, 'atq')),
        'cri': round(media(mei, 'cri')),
        'def': round(media(dfs, 'def', pesos_def)),
        'gol': round(media(gol, 'gol')) if gol else 20,
    }


def escalar(time, formacao, titulares=None):
    """ Escolhe os 11 da formação: usa `titulares` (nomes) quando válidos; senão o melhor por posição. """
    elenco = time['elenco']
    slots = FORMACOES[formacao]
    por_nome = {j['nome']: j for j in elenco}
    if titulares and len(titulares) == 11 and all(n in por_nome for n in titulares) and len(set(titulares)) == 11:
        return [por_nome[n] for n in titulares]
    livres = list(elenco)
    escolhidos = [None] * len(slots)
    # 1ª passada: quem joga na própria posição (melhor nota primeiro)
    for i, slot in enumerate(slots):
        naturais = [j for j in livres if j['pos'] == slot]
        if naturais:
            escolhidos[i] = max(naturais, key=lambda j: j['nota'])
            livres.remove(escolhidos[i])
    # 2ª passada: vagas sem especialista recebem o melhor adaptado
    for i, slot in enumerate(slots):
        if escolhidos[i] is None:
            melhor = max(livres, key=lambda j: j['nota'] - custo_posicao(j['pos'], slot))
            livres.remove(melhor)
            escolhidos[i] = melhor
    return escolhidos


def titulares_padrao(time, formacao):
    return [j['nome'] for j in escalar(time, formacao)]


TIMES = {t[0]: _montar(*t) for t in _TIMES}
FREGUESES = {t[0]: _montar(*t) for t in _FREGUESES}
for _t in FREGUESES.values():
    _t['freguesa'] = True
    _t['nome'] = _t['clube']


def todos():
    return sorted(TIMES.values(), key=lambda t: (-t['overall'], t['nome']))


def obter(chave):
    return TIMES.get(chave) or FREGUESES.get(chave)


def fregueses():
    return list(FREGUESES.values())

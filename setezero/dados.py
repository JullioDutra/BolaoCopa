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
    ('gre-1995', 'Grêmio', 1995, 'A Libertadores do Jardel', '#0d80bf', '4-4-2', 'Luiz Felipe Scolari',
     'Danrlei,GOL,84;Arce,LAT,80;Adílson,ZAG,78;Rivarola,ZAG,77;Roger,LAT,75;Dinho,VOL,78;Goiano,VOL,78;'
     'Paulo Nunes,PON,84;Carlos Miguel,MEI,80;Jardel,ATA,88;Aílton,ATA,80;Luís Carlos Goiano,VOL,74;Régis,ZAG,72;Zé Alcino,ATA,74;Emerson,GOL,66'),
    ('gre-1983', 'Grêmio', 1983, 'O Mundial de Renato Portaluppi', '#0d80bf', '4-3-3', 'Valdir Espinosa',
     'Mazaropi,GOL,80;Paulo César,LAT,76;De León,ZAG,86;Baidek,ZAG,76;Casemiro,LAT,76;China,VOL,76;Osvaldo,MEI,78;'
     'César,MEI,80;Renato Gaúcho,PON,88;Tarciso,PON,84;Caio,ATA,78;Leandro,LAT,72;Paulo Roberto,ZAG,72;Bonamigo,GOL,64;Eder,MEI,72'),
    ('san-2011', 'Santos', 2011, 'O Santos de Neymar e Ganso', '#1a1a1a', '4-3-3', 'Muricy Ramalho',
     'Rafael,GOL,80;Danilo,LAT,80;Edu Dracena,ZAG,78;Durval,ZAG,76;Léo,LAT,76;Arouca,VOL,79;Elano,MEI,82;'
     'Paulo Henrique Ganso,MEI,88;Neymar,PON,92;Borges,ATA,82;Zé Love,ATA,74;Alan Kardec,ATA,76;Adriano,VOL,74;Henrique,ZAG,74;Aranha,GOL,66'),
    ('spa-1992', 'São Paulo', 1992, 'O Bi da América', '#e30613', '4-4-2', 'Telê Santana',
     'Zetti,GOL,84;Vítor,LAT,76;Ronaldão,ZAG,79;Ricardo Rocha,ZAG,82;Ivan,LAT,74;Pintado,VOL,78;Cafu,LAT,84;'
     'Raí,MEI,92;Palhinha,MEI,82;Müller,ATA,84;Macedo,ATA,76;Toninho Cerezo,VOL,78;Adílson,VOL,74;Careca,ATA,80;Gilmar Rinaldi,GOL,66'),
    ('fla-2009', 'Flamengo', 2009, 'O Hexa do Imperador', '#c8102e', '4-4-2', 'Andrade',
     'Bruno,GOL,78;Léo Moura,LAT,80;Álvaro,ZAG,78;Ronaldo Angelim,ZAG,78;Juan,LAT,80;Willians,VOL,78;Toró,VOL,74;'
     'Petkovic,MEI,84;Ibson,MEI,76;Adriano,ATA,88;Zé Roberto,ATA,74;Kléberson,MEI,78;David,ATA,72;Fábio Luciano,ZAG,74;Marcelo Lomba,GOL,66'),
    ('cor-2005', 'Corinthians', 2005, 'O Time do Tevez', '#1a1a1a', '4-4-2', 'Tite',
     'Fábio Costa,GOL,80;Coelho,LAT,74;Betão,ZAG,76;Marcelo Mattos,VOL,76;Gustavo Nery,LAT,76;Bobô,MEI,76;Carlos Alberto,MEI,82;'
     'Roger,MEI,78;Tevez,ATA,90;Nilmar,ATA,84;Gil,ATA,74;Fabinho,VOL,72;Sebá,ZAG,72;Marinho,PON,76;Gustavo,GOL,64'),
    ('int-1975', 'Internacional', 1975, 'O Colorado Invencível', '#e5050f', '4-3-3', 'Rubens Minelli',
     'Manga,GOL,84;Valdomiro,PON,84;Figueroa,ZAG,92;Marinho Peres,ZAG,82;Hermínio,LAT,78;Caçapava,VOL,78;Falcão,MEI,92;'
     'Escurinho,ATA,82;Lula,PON,80;Batista,VOL,76;Dario,ATA,82;Cláudio,MEI,74;Vacaria,LAT,72;Carlos,ATA,72;Benitez,GOL,64'),
    ('cru-1966', 'Cruzeiro', 1966, 'A Máquina de Tostão', '#0033a0', '4-3-3', 'Ayrton Moreira',
     'Raul,GOL,80;Pedro Paulo,LAT,74;William,ZAG,76;Procópio,ZAG,78;Neco,LAT,74;Piazza,VOL,86;Hilton Oliveira,MEI,76;'
     'Dirceu Lopes,MEI,90;Tostão,ATA,94;Natal,PON,78;Evaldo,PON,80;Zé Carlos,ATA,74;Murilo,VOL,72;Raimundo,ZAG,70;Dida,GOL,62'),
    ('cam-2013', 'Atlético-MG', 2013, 'A Libertadores do Ronaldinho', '#1a1a1a', '4-2-3-1', 'Cuca',
     'Victor,GOL,88;Marcos Rocha,LAT,78;Réver,ZAG,80;Léo Silva,ZAG,76;Júnior César,LAT,74;Pierre,VOL,78;Josué,VOL,78;'
     'Ronaldinho Gaúcho,MEI,90;Tardelli,PON,82;Jô,ATA,80;Guilherme,PON,76;Bernard,PON,82;Leonardo Silva,ZAG,74;Richarlyson,VOL,74;Giovanni,GOL,64'),
    ('bot-1995', 'Botafogo', 1995, 'O Campeão do Túlio', '#1a1a1a', '4-4-2', 'Paulo Autuori',
     'Wagner,GOL,80;Wilson Goiano,LAT,74;Gonçalves,ZAG,78;Wilson Gottardo,ZAG,76;Sérgio Manoel,LAT,74;Leandro Ávila,VOL,76;Moisés,MEI,78;'
     'Rogério,MEI,76;Túlio Maravilha,ATA,88;Donizete Pantera,ATA,82;André Silva,ATA,72;Jéferson,PON,76;Marcelo Camacho,VOL,72;Mauro,ZAG,70;Perez,GOL,64'),
    ('bot-1962', 'Botafogo', 1962, 'O Botafogo de Garrincha', '#1a1a1a', '4-3-3', 'Paulo Amaral',
     'Manga,GOL,84;Rildo,LAT,78;Zé Maria,ZAG,76;Nilton Santos,LAT,94;Zagallo,MEI,86;Didi,MEI,90;Amarildo,ATA,90;'
     'Garrincha,PON,98;Quarentinha,ATA,86;Jairzinho,PON,80;Gérson,MEI,86;Rildo II,LAT,70;Paulistinha,ZAG,74;Ayrton,GOL,64;Ferreira,ATA,70'),
    ('flu-1984', 'Fluminense', 1984, 'O Time de Romerito e Assis', '#9f0e2f', '4-3-3', 'Carlos Alberto Parreira',
     'Paulo Victor,GOL,80;Aldo,LAT,74;Duílio,ZAG,78;Ricardo Gomes,ZAG,84;Branco,LAT,82;Jandir,VOL,76;Delei,MEI,76;'
     'Romerito,MEI,86;Assis,ATA,84;Washington,ATA,82;Tato,PON,78;Leomir,ZAG,72;Vica,MEI,72;Deley,PON,74;Ricardo Pinto,GOL,62'),
    ('vas-2000', 'Vasco', 2000, 'A Copa Mercosul do Romário', '#1a1a1a', '4-4-2', 'Antônio Lopes',
     'Hélton,GOL,78;Clébson,LAT,74;Odvan,ZAG,76;Mauro Galvão,ZAG,78;Gilberto,LAT,76;Juninho Paulista,MEI,82;Márcio Santos,VOL,76;'
     'Juninho Pernambucano,MEI,86;Euller,PON,80;Romário,ATA,94;Edmundo,ATA,88;Pedrinho,MEI,76;Jorginho Paulista,VOL,72;Felipe,LAT,74;Hélio,GOL,62'),
    ('pal-1993', 'Palmeiras', 1993, 'O Fim do Jejum', '#006437', '4-4-2', 'Vanderlei Luxemburgo',
     'Velloso,GOL,80;Mazinho,LAT,76;Antônio Carlos,ZAG,78;Cléber,ZAG,76;Roberto Carlos,LAT,86;Mauro Silva,VOL,82;Zinho,MEI,86;'
     'Rivaldo,MEI,88;Edílson,PON,84;Evair,ATA,88;Edmundo,ATA,88;Amaral,VOL,76;César Sampaio,VOL,80;Jorginho,LAT,74;Sérgio,GOL,64'),
    ('cru-2013', 'Cruzeiro', 2013, 'O Bicampeão Brasileiro', '#0033a0', '4-2-3-1', 'Marcelo Oliveira',
     'Fábio,GOL,84;Mayke,LAT,76;Dedé,ZAG,82;Léo,ZAG,76;Egídio,LAT,80;Nílton,VOL,80;Lucas Silva,VOL,78;'
     'Everton Ribeiro,MEI,88;Ricardo Goulart,ATA,86;Willian,PON,78;Júlio Baptista,ATA,76;Marcelo Moreno,ATA,78;Dagoberto,PON,76;Souza,VOL,74;Rafael,GOL,62'),
    ('cap-2001', 'Athletico-PR', 2001, 'O Furacão Campeão', '#c8102e', '4-4-2', 'Geninho',
     'Flávio,GOL,76;Nem,LAT,72;Gustavo,ZAG,76;Antônio Carlos,ZAG,76;Cocito,LAT,72;Adriano Gabiru,VOL,74;Kléberson,VOL,80;'
     'Alex Mineiro,ATA,82;Fernando,MEI,74;Jackson,ATA,76;Kleber,ATA,78;Cleisson,MEI,72;Rogério,MEI,70;Dagoberto,ATA,74;Edson,GOL,60'),
    ('spa-2005', 'São Paulo', 2005, 'O Mundial de 2005', '#e30613', '4-4-2', 'Paulo Autuori',
     'Rogério Ceni,GOL,90;Cicinho,LAT,80;Fabão,ZAG,78;Lugano,ZAG,84;Júnior,LAT,78;Mineiro,VOL,80;Josué,VOL,80;'
     'Danilo,MEI,86;Souza,MEI,78;Amoroso,ATA,82;Aloísio,ATA,80;Diego Tardelli,ATA,72;Thiago,PON,72;Alex,ZAG,72;Bosco,GOL,64'),
    ('san-1970', 'Santos', 1970, 'O Santos de Pelé 1970', '#1a1a1a', '4-3-3', 'Antoninho',
     'Cláudio,GOL,76;Carlos Alberto Torres,LAT,90;Ramos Delgado,ZAG,84;Joel Camargo,ZAG,80;Rildo,LAT,76;Clodoaldo,VOL,84;Lima,MEI,78;'
     'Pelé,ATA,98;Edu,PON,82;Toninho Guerreiro,ATA,80;Manuel Maria,PON,76;Zé Carlos,VOL,70;Mauro,ZAG,70;Gilmar,GOL,72;Pepe,PON,78'),
    ('for-2023', 'Fortaleza', 2023, 'O Leão do Pici', '#0033a0', '4-3-3', 'Juan Pablo Vojvoda',
     'João Ricardo,GOL,76;Tinga,LAT,74;Titi,ZAG,76;Brítez,ZAG,76;Bruno Pacheco,LAT,74;Zé Welison,VOL,74;Pochettino,MEI,76;'
     'Lucas Sasha,MEI,76;Moisés,PON,78;Yago Pikachu,PON,78;Lucero,ATA,80;Marinho,PON,76;Kervin Andrade,MEI,72;Caio Alexandre,VOL,74;Marcelo Boeck,GOL,66'),
    ('bah-1988', 'Bahia', 1988, 'O Tricolor de Aço', '#0033a0', '4-4-2', 'Evaristo de Macedo',
     'Ronaldo,GOL,76;Paulo Rodrigues,LAT,72;Cláudio Mineiro,ZAG,74;Zé Carlos,ZAG,72;Tony,LAT,72;Zé Mário,VOL,74;Bobô,MEI,82;'
     'Charles,MEI,76;Sandro,PON,74;Marinho,ATA,76;Cipó,ATA,78;Paulo Rodrigues II,MEI,70;Bobô Jr,ATA,70;Gil,VOL,70;Jean,GOL,60'),
    ('fla-2022', 'Flamengo', 2022, 'A Terceira Libertadores', '#c8102e', '4-2-3-1', 'Dorival Júnior',
     'Santos,GOL,80;Rodinei,LAT,78;Léo Pereira,ZAG,80;David Luiz,ZAG,80;Filipe Luís,LAT,83;Thiago Maia,VOL,78;João Gomes,VOL,80;'
     'Arrascaeta,MEI,87;Éverton Ribeiro,PON,82;Gabigol,ATA,88;Pedro,ATA,85;Bruno Henrique,PON,83;Gerson,MEI,84;Marinho,PON,80;Diego Alves,GOL,76'),
    ('cor-2015', 'Corinthians', 2015, 'O Hepta de Tite', '#1a1a1a', '4-1-4-1', 'Tite',
     'Cássio,GOL,85;Fágner,LAT,78;Gil,ZAG,80;Felipe,ZAG,78;Uendel,LAT,76;Ralf,VOL,82;Elias,MEI,80;Jádson,MEI,82;'
     'Renato Augusto,MEI,85;Malcom,PON,76;Vagner Love,ATA,80;Rodriguinho,MEI,76;Lucca,ATA,72;Edílson,LAT,74;Walter,GOL,66'),
    ('pal-2018', 'Palmeiras', 2018, 'O Time do Felipão', '#006437', '4-2-3-1', 'Luiz Felipe Scolari',
     'Weverton,GOL,82;Mayke,LAT,78;Luan,ZAG,78;Antônio Carlos,ZAG,78;Victor Luis,LAT,74;Felipe Melo,VOL,82;Bruno Henrique,VOL,78;'
     'Lucas Lima,MEI,80;Moisés,MEI,80;Dudu,PON,86;Willian,PON,80;Deyverson,ATA,76;Gustavo Scarpa,MEI,80;Borja,ATA,78;Jailson,GOL,70'),
    ('spa-2008', 'São Paulo', 2008, 'O Tri Brasileiro do Muricy', '#e30613', '4-4-2', 'Muricy Ramalho',
     'Rogério Ceni,GOL,90;Zé Luís,ZAG,76;Miranda,ZAG,80;Breno,ZAG,78;Jorge Wagner,LAT,76;Hernanes,MEI,86;Jean,VOL,78;'
     'Joílson,VOL,78;Dagoberto,PON,82;Borges,ATA,84;Aloísio,ATA,78;Richarlyson,LAT,76;Hugo,LAT,76;André Dias,ZAG,76;Bosco,GOL,66'),
    ('san-2010', 'Santos', 2010, 'Os Meninos da Copa do Brasil', '#1a1a1a', '4-3-3', 'Dorival Júnior',
     'Felipe,GOL,78;Pará,LAT,76;Durval,ZAG,78;Edu Dracena,ZAG,78;Léo,LAT,76;Arouca,VOL,78;Wesley,VOL,80;'
     'Paulo Henrique Ganso,MEI,88;Neymar,PON,90;André,ATA,82;Robinho,PON,88;Marquinhos,MEI,74;Alan Patrick,MEI,74;Rafael Moura,ATA,74;Rafael,GOL,64'),
    ('col-2010', 'Internacional', 2010, 'A Bi da América', '#e5050f', '4-2-3-1', 'Celso Roth',
     'Renan,GOL,80;Nei,LAT,76;Bolívar,ZAG,78;Índio,ZAG,78;Kléber,LAT,76;Guiñazú,VOL,80;Sandro,VOL,80;'
     'D\'Alessandro,MEI,88;Giuliano,MEI,76;Taison,PON,80;Rafael Sóbis,ATA,82;Tinga,VOL,78;Alecsandro,ATA,80;Walter,ATA,76;Lauro,GOL,66'),
    ('cam-1977', 'Atlético-MG', 1977, 'O Campeão Moral de Reinaldo', '#1a1a1a', '4-3-3', 'Barbatana',
     'João Leite,GOL,86;Orlando,LAT,78;Luisinho,ZAG,84;Osmar,ZAG,78;Jorge Valença,LAT,76;Toninho Cerezo,VOL,90;Paulo Isidoro,MEI,84;'
     'Chicão,MEI,78;Reinaldo,ATA,94;Éder Aleixo,PON,86;Ziza,ATA,80;Heleno,PON,76;Vanderlei,ZAG,74;Humberto,LAT,72;Raul,GOL,66'),
    ('cru-1997', 'Cruzeiro', 1997, 'O Campeão da Libertadores 97', '#0033a0', '4-4-2', 'Paulo Autuori',
     'Dida,GOL,86;Wilson Gottardo,ZAG,78;Gelson Baresi,ZAG,78;Cleisson,LAT,76;Vítor,LAT,74;Ricardinho,VOL,80;Nonato,VOL,76;'
     'Elivélton,MEI,82;Palhinha,MEI,84;Fábio Júnior,ATA,86;Marcelo Ramos,ATA,80;Müller,PON,80;Donizete,ATA,76;Zinho,MEI,76;Paulo César,GOL,64'),
    ('flu-2010', 'Fluminense', 2010, 'O Tricampeão do Conca', '#9f0e2f', '4-4-2', 'Muricy Ramalho',
     'Fernando Henrique,GOL,78;Mariano,LAT,76;Gum,ZAG,78;Leandro Euzébio,ZAG,76;Júnior César,LAT,76;Diguinho,VOL,78;Marquinho,VOL,76;'
     'Deco,MEI,82;Conca,MEI,90;Fred,ATA,86;Emerson,PON,80;Washington,ATA,80;Rafael Moura,ATA,74;Edinho,VOL,74;Ricardo Berna,GOL,64'),
    ('cor-1990', 'Corinthians', 1990, 'O Time de Neto', '#1a1a1a', '4-4-2', 'Nelsinho Baptista',
     'Ronaldo,GOL,80;Giba,LAT,74;Marcelo,ZAG,78;Guinei,ZAG,76;Jacenir,LAT,74;Márcio,VOL,76;Wilson Mano,VOL,74;'
     'Neto,MEI,88;Fabinho,MEI,78;Tupãzinho,ATA,82;Mauro,ATA,76;Ezequiel,PON,72;Ney,MEI,72;Biro-Biro,MEI,74;Jairo,GOL,62'),
    ('gre-2021', 'Grêmio', 2021, 'O Imortal do Jardel Paulista', '#0d80bf', '4-3-3', 'Renato Gaúcho',
     'Vanderlei,GOL,76;Orejuela,LAT,74;Geromel,ZAG,82;Kannemann,ZAG,80;Diogo Barbosa,LAT,76;Villasanti,VOL,76;Lucas Silva,VOL,74;'
     'Douglas Costa,PON,82;Diego Souza,ATA,80;Jean Pyerre,MEI,78;Ferreira,ATA,78;Alisson,PON,78;Maicon,MEI,78;Rafinha,LAT,76;Paulo Victor,GOL,70'),
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

# O resto do mundo: grandes esquadrões europeus para a "Busca pelo Mundial" (mais fortes que qualquer time brasileiro)
_MUNDO = [
    ('bar-2012', 'Barcelona', 2012, 'O Tiki-Taka de Guardiola', '#a50044', '4-3-3', 'Pep Guardiola',
     'Valdés,GOL,86;Dani Alves,LAT,89;Piqué,ZAG,90;Puyol,ZAG,89;Jordi Alba,LAT,88;Busquets,VOL,92;Xavi,MEI,95;'
     'Iniesta,MEI,95;Pedro,PON,87;Messi,ATA,99;Alexis Sánchez,PON,88;Mascherano,ZAG,86;Fàbregas,MEI,89;Thiago,MEI,86;Pinto,GOL,72'),
    ('bar-2009', 'Barcelona', 2009, 'O Sextete', '#a50044', '4-3-3', 'Pep Guardiola',
     'Valdés,GOL,86;Dani Alves,LAT,88;Piqué,ZAG,88;Puyol,ZAG,90;Abidal,LAT,86;Yaya Touré,VOL,89;Xavi,MEI,94;'
     'Iniesta,MEI,94;Henry,PON,90;Eto\'o,ATA,91;Messi,PON,96;Keita,VOL,82;Márquez,ZAG,84;Bojan,ATA,78;Pinto,GOL,72'),
    ('rma-2002', 'Real Madrid', 2002, 'Os Galácticos', '#e5e5e5', '4-4-2', 'Vicente del Bosque',
     'Casillas,GOL,89;Salgado,LAT,86;Hierro,ZAG,89;Helguera,ZAG,82;Roberto Carlos,LAT,92;Makélélé,VOL,90;Figo,PON,93;'
     'Zidane,MEI,98;Raúl,ATA,92;Ronaldo,ATA,97;Solari,PON,84;Guti,MEI,86;McManaman,PON,82;Morientes,ATA,85;César,GOL,70'),
    ('rma-2017', 'Real Madrid', 2017, 'O Tri Consecutivo da Europa', '#e5e5e5', '4-3-3', 'Zinedine Zidane',
     'Navas,GOL,87;Carvajal,LAT,86;Sergio Ramos,ZAG,92;Varane,ZAG,89;Marcelo,LAT,90;Casemiro,VOL,90;Modric,MEI,93;'
     'Kroos,MEI,93;Bale,PON,90;Cristiano Ronaldo,ATA,98;Benzema,ATA,92;Isco,MEI,88;Asensio,PON,84;Nacho,ZAG,82;Kovacic,MEI,82'),
    ('mil-1989', 'Milan', 1989, 'O Milan de Sacchi', '#c8102e', '4-4-2', 'Arrigo Sacchi',
     'Galli,GOL,86;Tassotti,LAT,86;Baresi,ZAG,95;Costacurta,ZAG,87;Maldini,LAT,92;Colombo,PON,84;Ancelotti,VOL,88;'
     'Rijkaard,VOL,92;Donadoni,MEI,90;Gullit,ATA,96;Van Basten,ATA,98;Evani,MEI,82;Virdis,ATA,82;Filippo Galli,ZAG,82;Pazzagli,GOL,70'),
    ('mil-1994', 'Milan', 1994, 'Os Invencíveis de Capello', '#c8102e', '4-4-2', 'Fabio Capello',
     'Rossi,GOL,86;Tassotti,LAT,86;Baresi,ZAG,94;Costacurta,ZAG,88;Maldini,LAT,94;Albertini,VOL,87;Desailly,VOL,91;'
     'Donadoni,MEI,89;Savicevic,MEI,93;Massaro,ATA,86;Papin,ATA,86;Panucci,LAT,82;Boban,MEI,88;Simone,ATA,80;Antonioli,GOL,70'),
    ('mil-2007', 'Milan', 2007, 'O Milan de Kaká', '#c8102e', '4-3-1-2', 'Carlo Ancelotti',
     'Dida,GOL,86;Cafu,LAT,88;Nesta,ZAG,92;Maldini,ZAG,90;Jankulovski,LAT,82;Gattuso,VOL,86;Pirlo,MEI,93;'
     'Seedorf,MEI,88;Kaká,MEI,96;Inzaghi,ATA,86;Gilardino,ATA,84;Ambrosini,VOL,84;Ronaldo,ATA,90;Oddo,LAT,80;Kalac,GOL,70'),
    ('bay-2013', 'Bayern de Munique', 2013, 'O Tríplice do Heynckes', '#dc052d', '4-2-3-1', 'Jupp Heynckes',
     'Neuer,GOL,94;Lahm,LAT,92;Boateng,ZAG,87;Dante,ZAG,85;Alaba,LAT,88;Javi Martínez,VOL,88;Schweinsteiger,VOL,91;'
     'Robben,PON,93;Müller,MEI,88;Ribéry,PON,93;Mandžukić,ATA,88;Kroos,MEI,89;Gómez,ATA,84;Shaqiri,PON,82;Starke,GOL,72'),
    ('bay-2020', 'Bayern de Munique', 2020, 'O Sextete de Flick', '#dc052d', '4-2-3-1', 'Hansi Flick',
     'Neuer,GOL,93;Kimmich,LAT,91;Boateng,ZAG,86;Alaba,ZAG,89;Davies,LAT,88;Goretzka,VOL,88;Thiago,MEI,90;'
     'Gnabry,PON,88;Müller,MEI,90;Lewandowski,ATA,97;Coman,PON,87;Perišić,PON,85;Süle,ZAG,84;Tolisso,MEI,82;Ulreich,GOL,70'),
    ('mun-1999', 'Manchester United', 1999, 'O Tríplice de Ferguson', '#da291c', '4-4-2', 'Alex Ferguson',
     'Schmeichel,GOL,88;Gary Neville,LAT,84;Stam,ZAG,89;Johnsen,ZAG,84;Irwin,LAT,84;Beckham,PON,92;Keane,VOL,92;'
     'Scholes,MEI,90;Giggs,PON,91;Cole,ATA,89;Yorke,ATA,90;Sheringham,ATA,86;Solskjær,ATA,85;Blomqvist,PON,80;Van der Gouw,GOL,70'),
    ('mun-2008', 'Manchester United', 2008, 'O Time de Cristiano Ronaldo', '#da291c', '4-3-3', 'Alex Ferguson',
     'Van der Sar,GOL,88;Brown,LAT,82;Ferdinand,ZAG,89;Vidić,ZAG,90;Evra,LAT,87;Carrick,VOL,86;Hargreaves,VOL,84;'
     'Scholes,MEI,88;Cristiano Ronaldo,PON,97;Rooney,ATA,92;Tevez,ATA,88;Giggs,PON,86;Nani,PON,84;Anderson,MEI,82;Foster,GOL,70'),
    ('liv-2019', 'Liverpool', 2019, 'O Time de Klopp', '#c8102e', '4-3-3', 'Jürgen Klopp',
     'Alisson,GOL,91;Alexander-Arnold,LAT,90;Van Dijk,ZAG,94;Matip,ZAG,84;Robertson,LAT,89;Fabinho,VOL,89;Henderson,MEI,86;'
     'Wijnaldum,MEI,86;Salah,PON,94;Firmino,ATA,88;Mané,PON,92;Milner,MEI,82;Origi,ATA,80;Gomez,ZAG,82;Adrián,GOL,70'),
    ('int-2010', 'Inter de Milão', 2010, 'O Tríplice de Mourinho', '#0033a0', '4-2-3-1', 'José Mourinho',
     'Júlio César,GOL,90;Maicon,LAT,90;Lúcio,ZAG,90;Samuel,ZAG,90;Chivu,LAT,84;Zanetti,VOL,88;Cambiasso,VOL,88;'
     'Sneijder,MEI,93;Eto\'o,PON,92;Milito,ATA,93;Pandev,PON,84;Motta,MEI,84;Stanković,MEI,84;Cordoba,ZAG,80;Toldo,GOL,72'),
    ('aja-1995', 'Ajax', 1995, 'Os Meninos de Van Gaal', '#d2122e', '4-3-3', 'Louis van Gaal',
     'Van der Sar,GOL,88;Reiziger,LAT,82;Blind,ZAG,88;Rijkaard,ZAG,88;F. de Boer,ZAG,86;Davids,VOL,88;Seedorf,MEI,88;'
     'Litmanen,MEI,92;Overmars,PON,89;Kluivert,ATA,88;Finidi George,PON,86;R. de Boer,MEI,86;Kanu,ATA,84;Bogarde,LAT,80;Menzo,GOL,70'),
    ('aja-1972', 'Ajax', 1972, 'O Futebol Total', '#d2122e', '4-3-3', 'Rinus Michels',
     'Stuy,GOL,82;Suurbier,LAT,86;Blankenburg,ZAG,86;Hulshoff,ZAG,86;Krol,LAT,90;Neeskens,VOL,92;Haan,MEI,90;'
     'Mühren,MEI,88;Rep,PON,88;Cruyff,ATA,99;Keizer,PON,90;Swart,PON,82;Muhren II,MEI,80;Mansveld,GOL,68;Baars,ZAG,76'),
    ('juv-1996', 'Juventus', 1996, 'A Velha Senhora de Lippi', '#e5e5e5', '4-3-3', 'Marcello Lippi',
     'Peruzzi,GOL,88;Torricelli,LAT,84;Ferrara,ZAG,88;Vierchowod,ZAG,86;Pessotto,LAT,82;Deschamps,VOL,88;Paulo Sousa,VOL,86;'
     'Di Livio,MEI,82;Del Piero,PON,93;Vialli,ATA,88;Ravanelli,ATA,88;Jugović,MEI,86;Padovano,ATA,82;Tacchinardi,VOL,80;Rampulla,GOL,70'),
    ('mci-2023', 'Manchester City', 2023, 'O Tríplice de Guardiola', '#6cabdd', '4-3-3', 'Pep Guardiola',
     'Ederson,GOL,90;Walker,LAT,88;Rúben Dias,ZAG,92;Akanji,ZAG,86;Aké,LAT,86;Rodri,VOL,95;Gündoğan,MEI,88;'
     'De Bruyne,MEI,96;Bernardo Silva,PON,92;Haaland,ATA,97;Foden,PON,90;Grealish,PON,88;Stones,ZAG,88;Álvarez,ATA,84;Ortega,GOL,72'),
    ('ars-2004', 'Arsenal', 2004, 'Os Invencíveis', '#ef0107', '4-4-2', 'Arsène Wenger',
     'Lehmann,GOL,84;Lauren,LAT,84;Campbell,ZAG,88;Kolo Touré,ZAG,86;Ashley Cole,LAT,90;Vieira,VOL,93;Gilberto Silva,VOL,88;'
     'Pirès,PON,90;Ljungberg,PON,88;Bergkamp,ATA,92;Henry,ATA,97;Reyes,PON,82;Edu,MEI,82;Cygan,ZAG,76;Almunia,GOL,72'),
    ('rma-1960', 'Real Madrid', 1960, 'O Real de Di Stéfano e Puskás', '#e5e5e5', '4-2-4', 'Miguel Muñoz',
     'Domínguez,GOL,84;Marquitos,LAT,84;Santamaría,ZAG,92;Pachín,ZAG,84;Vidal,LAT,82;Zárraga,VOL,84;Del Sol,VOL,88;'
     'Canário,PON,86;Di Stéfano,ATA,98;Puskás,ATA,97;Gento,PON,94;Mateos,MEI,80;Herrera,ZAG,78;Araquistáin,GOL,70;Rial,ATA,88'),
    ('nap-1987', 'Napoli', 1987, 'O Napoli de Maradona', '#12a0d7', '4-4-2', 'Ottavio Bianchi',
     'Garella,GOL,82;Ferrara,LAT,84;Ferrario,ZAG,82;Francini,LAT,82;Bruscolotti,ZAG,78;Bagni,VOL,84;De Napoli,VOL,84;'
     'Romano,MEI,84;Maradona,MEI,99;Giordano,ATA,88;Carnevale,ATA,86;Carannante,MEI,76;Renica,ZAG,82;Caffarelli,LAT,74;Di Fusco,GOL,66'),
    ('bar-1992', 'Barcelona', 1992, 'O Dream Team de Cruyff', '#a50044', '3-4-3', 'Johan Cruyff',
     'Zubizarreta,GOL,86;Ferrer,LAT,84;Koeman,ZAG,92;Nadal,ZAG,84;Serna,LAT,80;Guardiola,VOL,90;Eusébio,VOL,82;'
     'Bakero,MEI,86;Laudrup,MEI,93;Stoichkov,ATA,94;Salinas,ATA,86;Amor,MEI,84;Begiristain,PON,86;Goikoetxea,ZAG,80;Busquets,GOL,70'),
    ('bar-2015', 'Barcelona', 2015, 'O Tridente MSN', '#a50044', '4-3-3', 'Luis Enrique',
     'Ter Stegen,GOL,88;Dani Alves,LAT,87;Piqué,ZAG,88;Mascherano,ZAG,86;Jordi Alba,LAT,88;Busquets,VOL,91;Rakitić,MEI,88;'
     'Iniesta,MEI,92;Messi,PON,99;Suárez,ATA,94;Neymar,PON,93;Xavi,MEI,86;Mathieu,ZAG,80;Rafinha,MEI,80;Bravo,GOL,78'),
    ('rma-2014', 'Real Madrid', 2014, 'A Décima', '#e5e5e5', '4-3-3', 'Carlo Ancelotti',
     'Casillas,GOL,90;Carvajal,LAT,84;Sergio Ramos,ZAG,92;Varane,ZAG,86;Coentrão,LAT,84;Xabi Alonso,VOL,91;Modric,MEI,90;'
     'Di María,MEI,91;Bale,PON,92;Benzema,ATA,92;Cristiano Ronaldo,ATA,98;Isco,MEI,86;Pepe,ZAG,86;Khedira,VOL,86;Diego López,GOL,76'),
    ('int-1965', 'Inter de Milão', 1965, 'A Grande Inter', '#0033a0', '4-3-3', 'Helenio Herrera',
     'Sarti,GOL,84;Burgnich,LAT,88;Facchetti,LAT,94;Guarneri,ZAG,86;Picchi,ZAG,88;Bedin,VOL,82;Corso,MEI,90;'
     'Mazzola,MEI,92;Suárez,MEI,93;Jair,PON,90;Domenghini,PON,86;Peiró,ATA,86;Tagnin,VOL,78;Malatrasi,ZAG,76;Buffon,GOL,70'),
    ('bay-1976', 'Bayern de Munique', 1976, 'O Tri de Beckenbauer', '#dc052d', '4-4-2', 'Dettmar Cramer',
     'Maier,GOL,94;Hansen,LAT,84;Schwarzenbeck,ZAG,88;Beckenbauer,ZAG,98;Dürnberger,LAT,82;Roth,PON,88;Kapellmann,MEI,84;'
     'Weiss,MEI,82;Müller,ATA,96;Hoeneß,ATA,88;Rummenigge,ATA,88;Torstensson,PON,80;Andersson,MEI,78;Wunder,MEI,76;Rautiainen,GOL,70'),
    ('liv-1984', 'Liverpool', 1984, 'Os Reds da Era de Ouro', '#c8102e', '4-4-2', 'Joe Fagan',
     'Grobbelaar,GOL,86;Neal,LAT,86;Lawrenson,ZAG,88;Hansen,ZAG,90;Kennedy,LAT,86;Souness,VOL,92;Whelan,MEI,84;'
     'Lee,MEI,82;Dalglish,ATA,94;Rush,ATA,94;Johnston,PON,80;Nicol,MEI,82;Gillespie,ZAG,78;Robinson,ATA,76;Bolder,GOL,68'),
    ('che-2012', 'Chelsea', 2012, 'O Campeão Improvável de Londres', '#034694', '4-2-3-1', 'Roberto Di Matteo',
     'Cech,GOL,89;Ivanović,LAT,84;Cahill,ZAG,84;Terry,ZAG,88;Ashley Cole,LAT,88;Mikel,VOL,82;Lampard,MEI,90;'
     'Ramires,MEI,84;Mata,MEI,90;Drogba,ATA,92;Torres,ATA,84;Bertrand,LAT,76;Malouda,PON,82;Meireles,MEI,82;Turnbull,GOL,66'),
    ('ben-1962', 'Benfica', 1962, 'O Benfica de Eusébio', '#e50f1c', '4-2-4', 'Béla Guttmann',
     'Costa Pereira,GOL,86;Mário João,LAT,80;Germano,ZAG,86;Cruz,LAT,80;Ângelo,ZAG,82;Cavém,PON,86;Coluna,MEI,92;'
     'Águas,ATA,90;Eusébio,ATA,98;Simões,PON,88;Santana,ATA,82;Raul,GOL,66;José Augusto,PON,84;Mendes,MEI,76;Pedro,ZAG,70'),
    ('mun-1968', 'Manchester United', 1968, 'Os Trinitários', '#da291c', '4-4-2', 'Matt Busby',
     'Stepney,GOL,84;Brennan,LAT,80;Foulkes,ZAG,84;Stiles,VOL,86;Dunne,LAT,82;Crerand,MEI,86;Charlton,MEI,95;'
     'Best,PON,98;Law,ATA,94;Kidd,ATA,84;Aston,PON,82;Sadler,ATA,80;Fitzpatrick,MEI,74;Burns,ZAG,74;Rimmer,GOL,66'),
    ('por-2004', 'Porto', 2004, 'O Campeão de Mourinho', '#003893', '4-3-3', 'José Mourinho',
     'Vítor Baía,GOL,86;Paulo Ferreira,LAT,84;Ricardo Carvalho,ZAG,90;Jorge Costa,ZAG,84;Nuno Valente,LAT,84;Costinha,VOL,84;Maniche,MEI,88;'
     'Deco,MEI,92;Carlos Alberto,PON,84;Derlei,ATA,86;Pedro Mendes,MEI,82;McCarthy,ATA,80;Alenichev,MEI,80;Quaresma,PON,80;Nuno,GOL,66'),
]

# Times pequenos (fictícios) das fases iniciais da Copa do Brasil: mais fortes que os "fregueses", bem abaixo dos históricos
_PEQUENOS = [
    ('estrela-norte', 'Estrela do Norte EC', 0, 'A Zebra do Interior', '#0e7490', '4-4-2', 'Mestre Gil',
     'Zequinha,GOL,70;Dudu,LAT,67;Capitão,ZAG,69;Marrento,ZAG,68;Beto,LAT,66;Cabeça,VOL,69;Tonho,VOL,68;'
     'Léo Pelé,MEI,71;Maninho,MEI,69;Rei do Gol,ATA,72;Pardal,ATA,68;Banco 1,GOL,55;Banco 2,ZAG,57;Banco 3,MEI,58;Banco 4,ATA,58'),
    ('real-sertao', 'Real Sertão FC', 0, 'Os Cabras da Peste', '#a16207', '4-3-3', 'Seu Raimundo',
     'Chico,GOL,69;Baiano,LAT,66;Mourão,ZAG,68;Jegue,ZAG,67;Pedrão,LAT,65;Carcará,VOL,68;Sanfoneiro,MEI,70;'
     'Cabeção,MEI,68;Lampião,PON,71;Cangaço,ATA,70;Zabelê,PON,68;Banco 1,GOL,54;Banco 2,ZAG,56;Banco 3,MEI,57;Banco 4,ATA,57'),
    ('uniao-vila', 'União da Vila', 0, 'O Time do Povo', '#be185d', '4-4-2', 'Prof. Marquinhos',
     'Gomes,GOL,70;Bira,LAT,67;Salim,ZAG,69;Tadeu,ZAG,68;Paco,LAT,66;Vavá,VOL,69;Nenê,VOL,68;'
     'Jajá,MEI,71;Biel,MEI,69;Neto,ATA,72;Juca,ATA,69;Banco 1,GOL,55;Banco 2,ZAG,57;Banco 3,MEI,58;Banco 4,ATA,58'),
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
    '4-3-1-2': ['GOL', 'LAT', 'ZAG', 'ZAG', 'LAT', 'VOL', 'MEI', 'MEI', 'MEI', 'ATA', 'ATA'],
    '4-1-4-1': ['GOL', 'LAT', 'ZAG', 'ZAG', 'LAT', 'VOL', 'PON', 'MEI', 'MEI', 'PON', 'ATA'],
    '3-4-3': ['GOL', 'ZAG', 'ZAG', 'ZAG', 'LAT', 'VOL', 'VOL', 'LAT', 'PON', 'ATA', 'PON'],
    '4-2-4': ['GOL', 'LAT', 'ZAG', 'ZAG', 'LAT', 'VOL', 'VOL', 'PON', 'ATA', 'ATA', 'PON'],
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


def _montar(chave, clube, ano, apelido, cor, formacao, tecnico, elenco, ajuste=0):
    jogadores = []
    for item in elenco.split(';'):
        nome, pos, nota = item.rsplit(',', 2)
        jogadores.append(_jogador(nome.strip(), pos.strip(), int(nota) + ajuste))
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
PEQUENOS = {t[0]: _montar(*t) for t in _PEQUENOS}
AJUSTE_MUNDO = -3   # calibragem de dificuldade da Busca pelo Mundial (difícil, mas possível)
MUNDO = {t[0]: _montar(*t, ajuste=AJUSTE_MUNDO) for t in _MUNDO}
for _t in list(FREGUESES.values()) + list(PEQUENOS.values()):
    _t['freguesa'] = True
    _t['nome'] = _t['clube']


def todos():
    return sorted(TIMES.values(), key=lambda t: (-t['overall'], t['nome']))


def obter(chave):
    return TIMES.get(chave) or FREGUESES.get(chave) or PEQUENOS.get(chave) or MUNDO.get(chave)


def mundo():
    return sorted(MUNDO.values(), key=lambda t: (-t['overall'], t['nome']))


def pequenos():
    return list(FREGUESES.values()) + list(PEQUENOS.values())


def fregueses():
    return list(FREGUESES.values())

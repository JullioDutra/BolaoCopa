"""Frases de narração do "7 a 0" (PT-BR, tom de resenha)."""


def _e(rng, opcoes):
    return rng.choice(opcoes)


def gol(rng, nome, assist, time, pc, pf, penalti, gols_do_jogador):
    if penalti:
        base = _e(rng, [f"GOL! {nome} cobra o pênalti com frieza e balança a rede!",
                        f"É DELE! {nome} bate no canto e não dá chance pro goleiro!"])
    elif gols_do_jogador >= 3:
        base = f"HAT-TRICK! {nome} é o dono da noite! Que partida do camisa!"
    else:
        base = _e(rng, [f"GOOOOL! {nome} não perdoa e manda pro fundo do gol!",
                        f"AÍ ESTÁ! {nome} finaliza de primeira e a bola morre na rede!",
                        f"GOLAÇO! {nome} bate colocado, sem chance de defesa!",
                        f"É REDE! {nome} aparece livre e faz o {time} vibrar!",
                        f"{nome} cabeceia firme, no ângulo! Explode a torcida do {time}!"])
    if assist:
        base += _e(rng, [f" Passe açucarado de {assist}.", f" Assistência de {assist}.", f" {assist} serviu na medida."])
    return f"{base} ({pc}-{pf})"


def chute_fora(rng, nome, rival):
    return _e(rng, [f"{nome} arrisca de longe e a bola passa raspando a trave.",
                    f"{nome} chuta forte, mas manda por cima do gol do {rival}.",
                    f"Que chance! {nome} pega mal na bola e desperdiça.",
                    f"Bloqueio da zaga do {rival}! A bola sobra pra escanteio.",
                    f"{nome} tenta o drible e finaliza torto. Pra fora!"])


def defesa(rng, goleiro, atacante):
    return _e(rng, [f"Que defesa de {goleiro}! Salva o chute de {atacante}.",
                    f"{goleiro} espalma e evita o gol de {atacante}!",
                    f"Paredão! {goleiro} faz milagre depois da finalização de {atacante}.",
                    f"{atacante} bate firme e {goleiro} segura com segurança."])


def trave(rng, nome):
    return _e(rng, [f"NA TRAVE! {nome} carimba o poste e o estádio prende a respiração!",
                    f"Quase! {nome} acerta o travessão!"])


def desarme(rng, time):
    return _e(rng, [f"A defesa do {time} corta o perigo.", f"Desarme providencial do {time}, e o ataque morre ali.",
                    f"O {time} afasta a bola de qualquer jeito."])


def posse(rng, time):
    return _e(rng, [f"O {time} controla o jogo e roda a bola no meio-campo.", f"{time} trabalha a bola com paciência.",
                    f"Ritmo lento: o {time} procura espaços."])


def amarelo(rng, nome, time):
    return _e(rng, [f"Cartão amarelo para {nome} após entrada dura.", f"{nome} reclama e recebe o amarelo.",
                    f"O árbitro mostra o amarelo a {nome}, do {time}."])


def segundo_amarelo(rng, nome):
    return f"Segundo amarelo para {nome}! O árbitro aponta o vestiário."


def vermelho(rng, nome, time, direto):
    if direto:
        return f"VERMELHO DIRETO! {nome} acerta o adversário e o {time} fica com um a menos!"
    return f"{nome} está expulso e o {time} joga com 10!"


def lesao(rng, nome):
    return f"{nome} sente a coxa e pede para sair. Departamento médico em campo."


def substituicao(rng, entra, sai):
    return _e(rng, [f"Substituição: sai {sai}, entra {entra}.", f"Mexida no time! {entra} entra no lugar de {sai}."])


def tatica(rng, time, nova):
    return f"{time} muda o esquema: agora joga {nova.lower()}."


def penalti(rng, time):
    return f"PÊNALTI para o {time}! O árbitro marca a falta dentro da área!"


def penalti_perdido(rng, bat, gol):
    return _e(rng, [f"{gol} DEFENDE! {bat} desperdiça a cobrança!", f"Pra fora! {bat} isola o pênalti!"])


def apito_inicial(rng, casa, fora):
    return f"Rola a bola! {casa} x {fora} no maior clássico da resenha!"


def inicio_segundo_tempo(rng):
    return "Começa o segundo tempo!"


def intervalo(casa, fora, pc, pf):
    return f"Fim do primeiro tempo: {casa} {pc} x {pf} {fora}."


def fim_de_jogo(casa, fora, pc, pf):
    return f"Fim de papo! {casa} {pc} x {pf} {fora}."

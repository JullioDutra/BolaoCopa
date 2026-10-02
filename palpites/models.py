from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from django.db.models import Max
from decimal import Decimal
#from accounts.models import Transacao

# Cartola Coins ganhos por palpite certo
COINS_PLACAR_EXATO = 50
COINS_VENCEDOR = 10


class Jogo(models.Model):
    time_casa = models.CharField(max_length=100)    
    escudo_casa = models.ImageField(upload_to='escudos/', blank=True, null=True)
    time_fora = models.CharField(max_length=100)
    escudo_fora = models.ImageField(upload_to='escudos/', blank=True, null=True)
    data_hora = models.DateTimeField()
    gols_casa_real = models.IntegerField(null=True, blank=True)
    gols_fora_real = models.IntegerField(null=True, blank=True)
    finalizado = models.BooleanField(default=False)
    premio_distribuido = models.BooleanField(default=False)

    # --- Integração com API de resultados (football-data.org) ---
    campeonato = models.CharField(max_length=80, blank=True, help_text="Ex.: Brasileirão Série A")
    external_id = models.IntegerField(null=True, blank=True, unique=True, help_text="ID da partida na API (preenchido pelo sincronizador)")
    status_externo = models.CharField(max_length=20, blank=True, help_text="Status vindo da API: TIMED, IN_PLAY, FINISHED...")
    escudo_casa_url = models.URLField(max_length=300, blank=True)
    escudo_fora_url = models.URLField(max_length=300, blank=True)

    # --- Formato "Bolão da Rodada" ---
    rodada = models.ForeignKey('RodadaBolao', null=True, blank=True, on_delete=models.SET_NULL, related_name='jogos')

    @property
    def escudo_casa_src(self):
        """ URL do escudo: imagem enviada no Admin tem prioridade sobre a da API. """
        if self.escudo_casa:
            return self.escudo_casa.url
        from futebol.escudos import escudo_url
        return escudo_url(self.time_casa) or self.escudo_casa_url or None

    @property
    def escudo_fora_src(self):
        if self.escudo_fora:
            return self.escudo_fora.url
        from futebol.escudos import escudo_url
        return escudo_url(self.time_fora) or self.escudo_fora_url or None

    @property
    def ao_vivo(self):
        return self.status_externo in ('IN_PLAY', 'PAUSED') and not self.finalizado

    @property
    def fecha_em(self):
        """ Momento em que os palpites fecham (1h antes do jogo). """
        return self.data_hora - timedelta(hours=1)

    @property
    def aceita_palpite(self):
        """ Retorna True se faltar MAIS de 1 hora para o jogo começar """
        limite_para_apostar = self.data_hora - timedelta(hours=1)
        return timezone.now() < limite_para_apostar

    def calcular_pontuacao_palpites(self):
        """ Varre os palpites deste jogo e distribui os pontos """
        if not self.finalizado or self.gols_casa_real is None or self.gols_fora_real is None:
            return

        palpites = self.palpites.all()
        for palpite in palpites:
            pontos = 0
            
            # 1. Acerto Exato do placar (15 pontos)
            if palpite.gols_casa == self.gols_casa_real and palpite.gols_fora == self.gols_fora_real:
                pontos = 15
            else:
                # Descobre quem ganhou na vida real e no palpite
                vencedor_real = 'casa' if self.gols_casa_real > self.gols_fora_real else 'fora' if self.gols_fora_real > self.gols_casa_real else 'empate'
                vencedor_palpite = 'casa' if palpite.gols_casa > palpite.gols_fora else 'fora' if palpite.gols_fora > palpite.gols_casa else 'empate'

                # 2. Acertou o Vencedor ou Empate (5 pontos)
                if vencedor_real == vencedor_palpite:
                    pontos = 5

            # Salva a pontuação no palpite do usuário
            palpite.pontuacao_obtida = pontos
            palpite.save()

            # Cartola Coins por acerto (vale para todas as modalidades, creditado uma única vez)
            if pontos and not palpite.coins_creditados:
                from accounts import coins
                bonus = COINS_PLACAR_EXATO if pontos == 15 else COINS_VENCEDOR
                coins.creditar(
                    palpite.usuario, bonus,
                    f"⚽ {'Cravou' if pontos == 15 else 'Acertou o vencedor de'} {self.time_casa} x {self.time_fora}",
                )
                palpite.coins_creditados = True
                palpite.save(update_fields=['coins_creditados'])
                from avisos import atividade, conquistas
                if pontos == 15:
                    atividade.registrar(palpite.usuario, 'cravada',
                                        f"🎯 {atividade.nome_publico(palpite.usuario)} cravou {self.time_casa} {self.gols_casa_real} x {self.gols_fora_real} {self.time_fora}!",
                                        '/palpites/jogos/')
                conquistas.checar(palpite.usuario)

    def save(self, *args, **kwargs):
        # 1. Primeiro, salva as alterações do jogo no banco de dados
        super().save(*args, **kwargs)

        # 2. Se o jogo ACABOU, roda a regra dos pontos para todo mundo!
        if self.finalizado:
            self.calcular_pontuacao_palpites()

            # 2.1 Se o jogo faz parte de um Bolão da Rodada, vê se a rodada acabou
            if self.rodada_id:
                self.rodada.encerrar_se_possivel()

            # 3. Verifica se o prêmio AINDA NÃO FOI PAGO
            if not self.premio_distribuido:
                
                # Pega todos os palpites que valeram dinheiro
                palpites_pagos = self.palpites.filter(modalidade='pago')
                
                # Se não teve aposta paga, só trava o jogo e encerra
                if not palpites_pagos.exists():
                    self.premio_distribuido = True
                    super().save(update_fields=['premio_distribuido'])
                    return

                # Descobre qual foi a maior pontuação desse jogo (Quem são os vencedores?)
                maior_pontuacao = palpites_pagos.aggregate(Max('pontuacao_obtida'))['pontuacao_obtida__max']
                
                if maior_pontuacao and maior_pontuacao > 0:
                    # Filtra apenas a galera que cravou a maior pontuação
                    ganhadores = palpites_pagos.filter(pontuacao_obtida=maior_pontuacao)
                    qtd_ganhadores = ganhadores.count()
                    qtd_apostas = palpites_pagos.count()

                    # --- MATEMÁTICA FINANCEIRA ---
                    # Ex: 10 pessoas apostaram = R$ 100,00
                    total_arrecadado = Decimal(qtd_apostas) * Decimal('10.00')
                    
                    # Ex: Casa fica com 5% = R$ 5,00
                    taxa_casa = total_arrecadado * Decimal('0.05') 
                    
                    # Ex: Sobram R$ 95,00
                    premio_total = total_arrecadado - taxa_casa 
                    
                    # Ex: Divide pelos ganhadores
                    premio_individual = premio_total / Decimal(qtd_ganhadores) 

                    # Transação Segura: Só paga se não der nenhum erro no sistema
                    with transaction.atomic():
                        for palpite in ganhadores:
                            carteira = palpite.usuario.carteira
                            carteira.saldo += premio_individual
                            carteira.save()

                            # IMPORTAÇÃO LOCAL: Resolve o import circular e evita o NameError
                            from accounts.models import Transacao 

                            # Gera o extrato de recebimento para o usuário
                            Transacao.objects.create(
                                carteira=carteira,
                                tipo='premio',
                                valor=premio_individual,
                                descricao=f"🏆 Prêmio Bolão: {self.time_casa} x {self.time_fora} (Rateio entre {qtd_ganhadores} ganhador(es))"
                            )
                    
                # Por fim, tranca o cadeado para não pagar essa mesma partida duas vezes!
                self.premio_distribuido = True
                super().save(update_fields=['premio_distribuido'])

    def __str__(self):
        return f"{self.time_casa} x {self.time_fora}"


class Palpite(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='palpites')
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='palpites')
    gols_casa = models.IntegerField()
    gols_fora = models.IntegerField()
    modalidade = models.CharField(
        max_length=10,
        choices=[('resenha', 'Resenha'), ('pago', 'Pago'), ('rodada', 'Bolão da Rodada')],
        default='resenha',
    )
    pontuacao_obtida = models.IntegerField(default=0)
    coins_creditados = models.BooleanField(default=False, help_text="Já recebeu os Cartola Coins pelo acerto?")
    is_maior_pontuador = models.BooleanField(default=False, verbose_name="Maior pontuador da rodada?")

    class Meta:
        # Trava fundamental no banco: um usuário só pode ter UM palpite por jogo
        unique_together = ['usuario', 'jogo']

    def __str__(self):
        return f"{self.usuario.username}: {self.jogo.time_casa} {self.gols_casa} x {self.gols_fora} {self.jogo.time_fora} ({self.pontuacao_obtida} pts)"
        

class OscarCartolandia(models.Model):
    CATEGORIAS_CHOICES = [
        ('perola', '💩 Pérola do Ano (Maior Merda dita)'),
        ('cravacao', '🎯 Nostradamus (Cravação Máxima)'),
        ('zica', '🐈‍⬛ Zica Suprema (Falou e zicou o time)'),
        ('iludido', '🤡 Iludido do Ano'),
    ]

    indicado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='minhas_indicacoes')
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_CHOICES)
    autor = models.CharField(max_length=100, verbose_name="Filósofo/Autor")
    fala = models.TextField(verbose_name="A Aspa (O que o abençoado disse?)")
    nivel = models.IntegerField(default=5, verbose_name="Nível da Merda/Cravação (1 a 10)")
    print_prova = models.ImageField(upload_to='prints_oscar/', blank=True, null=True, verbose_name="Print (Contra fatos não há argumentos)")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.autor} - {self.get_categoria_display()}"

# ==========================================
# NOVOS MODELOS: ESTRUTURA PARA LONGO PRAZO
# ==========================================

class Clube(models.Model):
    COMPETICAO_CHOICES = [
        ('BRASILEIRAO', 'Brasileirão / Copa do Brasil'),
        ('EUROPA', 'Competições Europeias'),
    ]

    nome = models.CharField(max_length=100, unique=True)
    escudo = models.ImageField(upload_to='escudos/', blank=True, null=True)
    cor_hexadecimal = models.CharField(max_length=7, default='#FFFFFF', help_text="Ex: #FF0000 para vermelho")
    competicao = models.CharField(
        max_length=20,
        choices=COMPETICAO_CHOICES,
        default='BRASILEIRAO',
        help_text="Usado para filtrar o clube no formulário certo (Campeão BR/G4/Z4/CDB vs Campeão Europeu)."
    )

    def __str__(self):
        return self.nome

class Temporada(models.Model):
    ano = models.IntegerField(unique=True)
    ativa = models.BooleanField(default=True)
    prazo_brasileirao = models.DateTimeField(null=True, blank=True, help_text="Trava o Campeão, G4 e Z4")
    prazo_copas_fixas = models.DateTimeField(null=True, blank=True, help_text="Trava CDB e Europa") # <- Nome corrigido
    
    def brasileirao_aberto(self):
        if not self.prazo_brasileirao:
            return True
        return timezone.now() < self.prazo_brasileirao

    def copas_fixas_abertas(self):
        if not self.prazo_copas_fixas: # <- Agora bate com o campo
            return True
        return timezone.now() < self.prazo_copas_fixas
    
    def __str__(self):
        return f"Temporada {self.ano}"
        

class PalpiteLongoPrazo(models.Model):
    TIPO_CHOICES = [
        ('CAMPEAO_BR', 'Campeão Brasileirão'),
        ('G4', 'G4 Brasileirão'),
        ('Z4', 'Z4 Brasileirão'),
        ('CAMPEAO_EUROPA', 'Campeão Europeu (Champions)'),
        ('CAMPEAO_CDB', 'Campeão Copa do Brasil'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='palpites_longo_prazo')
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name='palpites')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)
    posicao_esperada = models.IntegerField(null=True, blank=True, help_text="Ex: 1 para campeão, 17 para Z4")
    pontos_obtidos = models.IntegerField(default=0)
    
    class Meta:
        # Evita que o usuário palpite o mesmo clube para a mesma posição duas vezes
        unique_together = ['usuario', 'temporada', 'tipo', 'clube']

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} - {self.clube.nome}"

class MuralCampeoes(models.Model):
    temporada = models.OneToOneField(Temporada, on_delete=models.CASCADE, related_name='campeao')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pontuacao_final = models.IntegerField()
    data_conquista = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"🏆 Campeão {self.temporada.ano}: {self.usuario.username}"

class TorneioLongoPrazo(models.Model):
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE, related_name='torneios_extras')
    nome = models.CharField(max_length=100, help_text="Ex: Campeão da Libertadores")
    icone = models.CharField(max_length=50, default="fa-trophy", help_text="Ícone FontAwesome (ex: fa-earth-americas)")
    pontos_premio = models.IntegerField(default=50)
    prazo_final = models.DateTimeField()
    
    def is_aberto(self):
        return timezone.now() < self.prazo_final

    def __str__(self):
        return f"{self.nome} - {self.temporada.ano}"

class PalpiteTorneioExtra(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    torneio = models.ForeignKey(TorneioLongoPrazo, on_delete=models.CASCADE)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'torneio')


# ==========================================
# FORMATO "BOLÃO DA RODADA"
# ==========================================

class RodadaBolao(models.Model):
    """
    Bolão que vale uma rodada inteira: o jogador paga UMA entrada e seus palpites
    em todos os jogos da rodada somam pontos. Quem fizer mais pontos leva o pote
    (empate divide). Convive com o formato clássico "por jogo" (R$ 10 por partida).
    """
    nome = models.CharField(max_length=120)
    campeonato = models.CharField(max_length=80, blank=True)
    numero = models.PositiveIntegerField(null=True, blank=True)
    valor_entrada = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('10.00'))
    taxa_casa = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.05'), help_text="0.05 = 5% do pote")
    premio_distribuido = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bolão da Rodada"
        verbose_name_plural = "Bolões da Rodada"
        ordering = ['-criada_em']

    def __str__(self):
        return self.nome

    @property
    def primeiro_jogo(self):
        return self.jogos.order_by('data_hora').first()

    @property
    def inscricoes_abertas(self):
        """ Dá para entrar até 1h antes do primeiro jogo da rodada. """
        primeiro = self.primeiro_jogo
        return bool(primeiro and primeiro.aceita_palpite and not self.premio_distribuido)

    @property
    def encerrada(self):
        jogos = self.jogos.all()
        return jogos.exists() and not jogos.filter(finalizado=False).exists()

    @property
    def pote(self):
        return self.valor_entrada * self.inscricoes.count()

    @property
    def premio_liquido(self):
        return (self.pote * (Decimal('1') - self.taxa_casa)).quantize(Decimal('0.01'))

    def ranking(self):
        """ [{'usuario', 'pontos', 'exatos', 'acertos'}] ordenado, só de quem está inscrito. """
        linhas = []
        for insc in self.inscricoes.select_related('usuario'):
            palpites = Palpite.objects.filter(
                usuario=insc.usuario, jogo__rodada=self, modalidade='rodada',
            )
            pontos = sum(p.pontuacao_obtida for p in palpites)
            linhas.append({
                'usuario': insc.usuario,
                'pontos': pontos,
                'exatos': sum(1 for p in palpites if p.pontuacao_obtida == 15),
                'acertos': sum(1 for p in palpites if p.pontuacao_obtida > 0),
                'palpites': palpites.count(),
            })
        linhas.sort(key=lambda l: (l['pontos'], l['exatos']), reverse=True)
        return linhas

    def encerrar_se_possivel(self):
        """ Quando o último jogo termina, paga o pote ao(s) líder(es). Idempotente. """
        if self.premio_distribuido or not self.encerrada:
            return False

        with transaction.atomic():
            rodada = RodadaBolao.objects.select_for_update().get(pk=self.pk)
            if rodada.premio_distribuido:
                return False

            ranking = rodada.ranking()
            if ranking and ranking[0]['pontos'] > 0:
                lider = ranking[0]['pontos']
                ganhadores = [l['usuario'] for l in ranking if l['pontos'] == lider]
                premio_individual = (rodada.premio_liquido / len(ganhadores)).quantize(Decimal('0.01'))

                from accounts.models import Transacao
                for usuario in ganhadores:
                    carteira = usuario.carteira
                    carteira.saldo += premio_individual
                    carteira.save()
                    Transacao.objects.create(
                        carteira=carteira, tipo='premio', valor=premio_individual,
                        descricao=f"🏆 Bolão da Rodada: {rodada.nome} ({lider} pts, rateio entre {len(ganhadores)})",
                    )
                    from avisos import atividade
                    atividade.registrar(usuario, 'rodada', f"🏆 {atividade.nome_publico(usuario)} levou o pote do {rodada.nome} com {lider} pts!",
                                        f"/palpites/rodada/{rodada.id}/")
            rodada.premio_distribuido = True
            rodada.save(update_fields=['premio_distribuido'])
        self.premio_distribuido = True
        return True


class InscricaoRodada(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscricoes_rodada')
    rodada = models.ForeignKey(RodadaBolao, on_delete=models.CASCADE, related_name='inscricoes')
    valor_pago = models.DecimalField(max_digits=8, decimal_places=2)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('usuario', 'rodada')]

    def __str__(self):
        return f"{self.usuario.username} em {self.rodada.nome}"

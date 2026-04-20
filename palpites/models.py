from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db import models, transaction
from django.db.models import Max
from decimal import Decimal
from django.utils import timezone
from accounts.models import Transacao

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

    @property
    def aceita_palpite(self):
        return timezone.now() < self.data_hora

    def calcular_pontuacao_palpites(self):
        """ Varre os palpites deste jogo e distribui os pontos """
        if not self.finalizado or self.gols_casa_real is None or self.gols_fora_real is None:
            return

        palpites = self.palpites.all()
        for palpite in palpites:
            pontos = 0
            
            # 1. Acerto Exato do placar (5 pontos)
            if palpite.gols_casa == self.gols_casa_real and palpite.gols_fora == self.gols_fora_real:
                pontos = 5
            else:
                # Descobre quem ganhou na vida real e no palpite
                vencedor_real = 'casa' if self.gols_casa_real > self.gols_fora_real else 'fora' if self.gols_fora_real > self.gols_casa_real else 'empate'
                vencedor_palpite = 'casa' if palpite.gols_casa > palpite.gols_fora else 'fora' if palpite.gols_fora > palpite.gols_casa else 'empate'

                # 2. Acertou o Vencedor (ou Empate)
                if vencedor_real == vencedor_palpite:
                    saldo_real = abs(self.gols_casa_real - self.gols_fora_real)
                    saldo_palpite = abs(palpite.gols_casa - palpite.gols_fora)
                    
                    # 3. Acertou Vencedor + Saldo de Gols (3 pontos)
                    if saldo_real == saldo_palpite:
                        pontos = 3
                    # 4. Acertou só o Vencedor (2 pontos)
                    else:
                        pontos = 2

            # Salva a pontuação no palpite do usuário
            palpite.pontuacao_obtida = pontos
            palpite.save()

    def save(self, *args, **kwargs):
        # Primeiro salva o jogo no banco
        super().save(*args, **kwargs)
        # Depois verifica se finalizou para rodar o cálculo
        if self.finalizado:
            self.calcular_pontuacao_palpites()

    def __str__(self):
        return f"{self.time_casa} x {self.time_fora}"
    
    @property
    def aceita_palpite(self):
        """ Retorna True se faltar MAIS de 24 horas para o jogo começar """
        limite_para_apostar = self.data_hora - timedelta(hours=24)
        return timezone.now() < limite_para_apostar
    
    def save(self, *args, **kwargs):
            # 1. Primeiro, salva as alterações do jogo no banco de dados
            super().save(*args, **kwargs)

            # 2. Verifica se o jogo ACABOU e se o prêmio AINDA NÃO FOI PAGO
            if self.finalizado and not self.premio_distribuido:
                
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
    
    

class Palpite(models.Model):
        usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='palpites')
        jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='palpites')
        gols_casa = models.IntegerField()
        gols_fora = models.IntegerField()
        pontuacao_obtida = models.IntegerField(default=0)
        modalidade = models.CharField(max_length=10, choices=[('resenha', 'Resenha'), ('pago', 'Pago')], default='resenha')
    
        class Meta:
        # Trava fundamental no banco: um usuário só pode ter UM palpite por jogo
         unique_together = ['usuario', 'jogo']

        def __str__(self):
         return f"{self.usuario.username}: {self.jogo.time_casa} {self.gols_casa} x {self.gols_fora} {self.jogo.time_fora} ({self.pontuacao_obtida} pts)"
        

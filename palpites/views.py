from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Max
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User


# Imports dos seus aplicativos
from bolao.decorators import acesso_liberado_required
from .models import Jogo, Palpite
from .forms import PalpiteForm
from accounts.models import Transacao

@acesso_liberado_required
def listar_jogos(request):
    # Busca todos os jogos ordenados pela data
    jogos = Jogo.objects.all().order_by('data_hora')
    
    # Busca todos os palpites que ESTE usuário já fez
    meus_palpites = Palpite.objects.filter(usuario=request.user)
    
    # Cria um dicionário rápido para não precisar ir ao banco várias vezes
    palpites_dict = {palpite.jogo.id: palpite for palpite in meus_palpites}
    
    # Anexa o palpite diretamente no objeto do jogo para o HTML ler facilmente
    for jogo in jogos:
        jogo.meu_palpite = palpites_dict.get(jogo.id)

        if jogo.finalizado and jogo.premio_distribuido:
            # Pega a pontuação máxima das apostas pagas deste jogo
            maior_pontuacao = Palpite.objects.filter(jogo=jogo, modalidade='pago').aggregate(Max('pontuacao_obtida'))['pontuacao_obtida__max']
            
            if maior_pontuacao is not None and maior_pontuacao > 0:
                jogo.ganhadores = Palpite.objects.filter(jogo=jogo, modalidade='pago', pontuacao_obtida=maior_pontuacao)
            else:
                jogo.ganhadores = []
        
    # --- LÓGICA DA BARRA LATERAL (Participantes) ---
    # Busca usuários que têm pelo menos um palpite na modalidade 'pago'
    jogadores_pago = User.objects.filter(palpites__modalidade='pago').distinct()
    # Busca usuários na 'resenha', mas remove da lista quem já aparece na lista 'pago'
    jogadores_resenha = User.objects.filter(palpites__modalidade='resenha').exclude(id__in=jogadores_pago).distinct()
        
    return render(request, 'palpites/listar_jogos.html', {
        'jogos': jogos,
        'jogadores_pago': jogadores_pago,
        'jogadores_resenha': jogadores_resenha
    })


@acesso_liberado_required
def fazer_palpite(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)

    # 1. Trava de segurança: O jogo já começou ou falta menos de 24h?
    if not jogo.aceita_palpite:
        messages.error(request, "Este jogo não aceita mais palpites. O prazo encerrou!")
        return redirect('palpites:listar_jogos')

    # Busca se o usuário já palpitou nesse jogo para carregar os dados na tela (Modo Edição)
    palpite_existente = Palpite.objects.filter(usuario=request.user, jogo=jogo).first()

    if request.method == 'POST':
        form = PalpiteForm(request.POST, instance=palpite_existente, jogo=jogo)
        
        # 2. Captura qual dos dois botões foi clicado na tela (Resenha ou Pago)
        tipo_aposta = request.POST.get('tipo_aposta', 'resenha') 
        
        if form.is_valid():
            palpite = form.save(commit=False)
            palpite.usuario = request.user
            palpite.jogo = jogo
            
            # Verifica se o palpite já era pago antes (para não cobrar R$10 novamente se ele só estiver editando o placar)
            ja_era_pago = palpite_existente and palpite_existente.modalidade == 'pago'
            
            # --- Lógica do Botão PAGO ---
            if tipo_aposta == 'pago' and not ja_era_pago:
                custo = Decimal('10.00')
                
                # Checa se tem saldo na carteira
                if request.user.carteira.saldo < custo:
                    messages.error(request, "Saldo insuficiente! Deposite R$ 10,00 ou jogue no Modo Resenha.")
                    return redirect('pagamentos:solicitar_deposito')
                
                # Transação Atômica: Só salva se não der erro no meio do caminho
                with transaction.atomic():
                    # Desconta o dinheiro
                    request.user.carteira.saldo -= custo
                    request.user.carteira.save()
                    
                    # Gera o comprovante no extrato
                    Transacao.objects.create(
                        carteira=request.user.carteira, 
                        tipo='aposta', 
                        valor=custo,
                        descricao=f"Palpite Valendo Prêmio: {jogo.time_casa} x {jogo.time_fora}"
                    )
                    
                    # Salva a aposta como paga
                    palpite.modalidade = 'pago'
                    palpite.save()
                    
                messages.success(request, "Palpite registrado Valendo Prêmio! (R$ 10,00 descontados)")
                
            # --- Lógica do Botão RESENHA (ou edição grátis de um palpite pago) ---
            else:
                # Se não era pago antes, salva como resenha
                if not ja_era_pago:
                    palpite.modalidade = 'resenha'
                
                palpite.save()
                
                # Feedback dinâmico
                if palpite_existente:
                    messages.success(request, "Seu palpite foi atualizado com sucesso!")
                else:
                    messages.success(request, "Palpite salvo na Resenha!")
                
            return redirect('palpites:listar_jogos')
    else:
        # Se não for POST (acabou de abrir a tela), carrega o form vazio ou preenchido com a aposta anterior
        form = PalpiteForm(instance=palpite_existente)

    return render(request, 'palpites/fazer_palpite.html', {
        'form': form, 
        'jogo': jogo,
        'palpite_existente': palpite_existente # <-- Vai dizer ao HTML se estamos Criando ou Editando
    })


@acesso_liberado_required
def ranking_geral(request):
    """ Soma a pontuação de todos os palpites agrupando por usuário e monta a tabela do ranking """
    
    ranking = Palpite.objects.values('usuario__username', 'usuario__first_name', 'usuario__participacao__tipo') \
        .annotate(total_pontos=Sum('pontuacao_obtida')) \
        .order_by('-total_pontos')
        
    return render(request, 'palpites/ranking.html', {'ranking': ranking})
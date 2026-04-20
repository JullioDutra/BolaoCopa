from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import datetime

from .models import Jogador, Convocacao
from .forms import ConvocacaoForm
from bolao.decorators import acesso_liberado_required
from accounts.models import Transacao

@acesso_liberado_required
def montar_selecao(request):
    # 1. Busca ou cria a convocação
    convocacao, created = Convocacao.objects.get_or_create(usuario=request.user)
    
    # 2. Lógica de Prazo (Trava dia 17 de Maio)
    ano_atual = timezone.now().year
    data_limite = timezone.make_aware(datetime.datetime(ano_atual, 5, 17, 23, 59, 59))
    prazo_encerrado = timezone.now() > data_limite
    
    # --- A GRANDE SACADA: Usar o histórico financeiro em vez da coluna ausente ---
    pagou_convocacao = Transacao.objects.filter(
        carteira=request.user.carteira, 
        descricao="Convocação Valendo Prêmio"
    ).exists()
    
    if request.method == 'POST':
        if prazo_encerrado:
            messages.error(request, "O prazo para convocações encerrou no dia 17 de Maio!")
            return redirect('dashboard')
            
        form = ConvocacaoForm(request.POST, instance=convocacao)
        tipo_aposta = request.POST.get('tipo_aposta', 'resenha')
        
        if form.is_valid():
            nova_convocacao = form.save(commit=False)
            
            # Se ele quer pagar AGORA, e AINDA NÃO PAGOU no passado
            if tipo_aposta == 'pago' and not pagou_convocacao:
                custo = Decimal('10.00')
                if request.user.carteira.saldo < custo:
                    messages.error(request, "Saldo insuficiente para o Modo Pago! Deposite R$10 ou salve como Resenha.")
                    return redirect('pagamentos:solicitar_deposito')
                
                with transaction.atomic():
                    request.user.carteira.saldo -= custo
                    request.user.carteira.save()
                    Transacao.objects.create(
                        carteira=request.user.carteira, tipo='aposta', valor=custo,
                        descricao="Convocação Valendo Prêmio"
                    )
                    nova_convocacao.save()
                    form.save_m2m()
                messages.success(request, "Convocação confirmada Valendo Prêmio! R$ 10,00 descontados.")
            else:
                # Se for resenha OU se ele já pagou antes, apenas salva a lista
                nova_convocacao.save()
                form.save_m2m()
                messages.success(request, "Convocação salva com sucesso!")
                
            return redirect('dashboard')
        else:
            messages.error(request, "Erro. Selecione exatamente 26 jogadores.")
    else:
        form = ConvocacaoForm(instance=convocacao)

    # 3. CONVERSÃO FORÇADA PARA LISTAS (Sua lógica perfeita de posições)
    jogadores_por_posicao = {
        'Goleiros': list(Jogador.objects.filter(posicao='Goleiro')),
        'Laterais': list(Jogador.objects.filter(posicao='Lateral')),
        'Zagueiros': list(Jogador.objects.filter(posicao='Zagueiro')),
        'Meias': list(Jogador.objects.filter(posicao='Meia')),
        'Atacantes': list(Jogador.objects.filter(posicao='Atacante')),
    }
    
    # Força a extração de IDs a ser uma lista de números
    convocados_lista = list(convocacao.jogadores.values_list('id', flat=True))

    return render(request, 'convocacao/montar_selecao.html', {
        'form': form, 
        'jogadores_por_posicao': jogadores_por_posicao,
        'convocados_ids': convocados_lista,
        'prazo_encerrado': prazo_encerrado
    })

@acesso_liberado_required
def ranking_convocacao(request):
    # Pega os IDs de todos os jogadores que você marcou como "Oficial" no Admin
    oficiais = set(Jogador.objects.filter(convocado_oficial=True).values_list('id', flat=True))
    
    # Pega todas as listas feitas pelos usuários
    convocacoes = Convocacao.objects.select_related('usuario').all()
    
    ranking = []
    for conv in convocacoes:
        # Pega os IDs que o usuário escolheu
        escolhidos = set(conv.jogadores.values_list('id', flat=True))
        
        # A matemática da interseção (quantos IDs batem entre a lista dele e a oficial)
        acertos = len(oficiais.intersection(escolhidos))
        
        ranking.append({
            'usuario': conv.usuario,
            'modalidade': conv.modalidade,
            'acertos': acertos
        })
        
    # Ordena do maior acertador para o menor
    ranking.sort(key=lambda x: x['acertos'], reverse=True)
    
    context = {
        'ranking': ranking,
        'total_oficiais': len(oficiais)
    }
    return render(request, 'convocacao/ranking_convocacao.html', context)
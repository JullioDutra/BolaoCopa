from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import datetime

from .models import Jogador, Convocacao
from .forms import ConvocacaoForm, SelecaoBrasileiraoForm
from bolao.decorators import acesso_liberado_required
from accounts.models import Transacao
from django.db.models import Count
from django.contrib.auth.decorators import login_required

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
    # 1. Pega os IDs de todos os jogadores que você marcou como "Oficial" no Admin
    oficiais = set(Jogador.objects.filter(convocado_oficial=True).values_list('id', flat=True))
    
    # 2. Pega todas as listas feitas pelos usuários
    convocacoes = Convocacao.objects.select_related('usuario').all()
    
    # Busca todas as transações de apostas de convocação de uma vez só para otimizar o banco de dados
    usuarios_pagos = set(Transacao.objects.filter(
        descricao="Convocação Valendo Prêmio"
    ).values_list('carteira__usuario_id', flat=True))
    
    ranking = []
    for conv in convocacoes:
        # Pega os IDs que o usuário escolheu
        escolhidos = set(conv.jogadores.values_list('id', flat=True))
        
        # A matemática da interseção (quantos IDs batem entre a lista dele e a oficial)
        acertos = len(oficiais.intersection(escolhidos))
        
        # Define a modalidade com base no histórico financeiro, contornando a ausência da coluna
        modalidade = 'pago' if conv.usuario.id in usuarios_pagos else 'resenha'
        
        ranking.append({
            'usuario': conv.usuario,
            'modalidade': modalidade,
            'acertos': acertos
        })
        
    # Ordena do maior acertador para o menor
    ranking.sort(key=lambda x: x['acertos'], reverse=True)
    
    context = {
        'ranking': ranking,
        'total_oficiais': len(oficiais)
    }
    return render(request, 'convocacao/ranking_convocacao.html', context)

@acesso_liberado_required
def estatisticas_convocacao(request):
    # 1. Total de usuários que submeteram uma convocação
    total_listas = Convocacao.objects.count()
    
    # 2. Busca os jogadores ordenados pelos mais escalados (M2M relation 'convocados')
    # Filtramos apenas os jogadores que foram escalados pelo menos 1 vez
    jogadores_mais_escalados = Jogador.objects.annotate(
        total_escalacoes=Count('convocados')
    ).filter(total_escalacoes__gt=0).order_by('-total_escalacoes')
    
    dados_jogadores = []
    for jogador in jogadores_mais_escalados:
        # Calcula a porcentagem de vezes que esse jogador apareceu nas listas
        porcentagem = (jogador.total_escalacoes / total_listas * 100) if total_listas > 0 else 0
        
        dados_jogadores.append({
            'jogador': jogador,
            'total_escalacoes': jogador.total_escalacoes,
            'porcentagem': round(porcentagem, 1),
            # O acerto aqui é binário com base no que você marcou no Admin
            'acertou_oficial': jogador.convocado_oficial  
        })
        
    context = {
        'dados_jogadores': dados_jogadores,
        'total_listas': total_listas
    }
    return render(request, 'convocacao/mais_escalados.html', context)


@login_required
def montar_selecao(request):
    convocacao, created = Convocacao.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        form = SelecaoBrasileiraoForm(request.POST)
        if form.is_valid():
            # Agrupa os 11 jogadores submetidos
            jogadores_selecionados = [
                form.cleaned_data['goleiro'],
                form.cleaned_data['defensor_1'], form.cleaned_data['defensor_2'], 
                form.cleaned_data['defensor_3'], form.cleaned_data['defensor_4'],
                form.cleaned_data['meia_1'], form.cleaned_data['meia_2'], form.cleaned_data['meia_3'],
                form.cleaned_data['atacante_1'], form.cleaned_data['atacante_2'], form.cleaned_data['atacante_3']
            ]
            
            # Validação estrita contra duplicação de jogadores
            if len(set(jogadores_selecionados)) != 11:
                messages.error(request, "Erro: Você não pode escalar o mesmo jogador em posições diferentes. Verifique duplicações no elenco.")
                return render(request, 'convocacao/montar_selecao.html', {'form': form})

            # Limpa o time antigo e salva o novo 4-3-3
            convocacao.jogadores.clear()
            for jogador in jogadores_selecionados:
                convocacao.jogadores.add(jogador)
                
            messages.success(request, "Seleção 4-3-3 confirmada com sucesso! ⚽")
            return redirect('montar_selecao')
            
    else:
        # Preenche o formulário se o usuário já tiver montado o time antes
        initial_data = {}
        jogadores_atuais = list(convocacao.jogadores.all())
        
        if len(jogadores_atuais) == 11:
            gols = [j for j in jogadores_atuais if j.posicao == 'Goleiro']
            defs = [j for j in jogadores_atuais if j.posicao == 'Defensor']
            meis = [j for j in jogadores_atuais if j.posicao == 'Meio-campista']
            atas = [j for j in jogadores_atuais if j.posicao == 'Atacante']
            
            if gols: initial_data['goleiro'] = gols[0]
            for i, d in enumerate(defs): initial_data[f'defensor_{i+1}'] = d
            for i, m in enumerate(meis): initial_data[f'meia_{i+1}'] = m
            for i, a in enumerate(atas): initial_data[f'atacante_{i+1}'] = a

        form = SelecaoBrasileiraoForm(initial=initial_data)

    return render(request, 'convocacao/montar_selecao.html', {
        'form': form,
        'convocacao': convocacao
    })

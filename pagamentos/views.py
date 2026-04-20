from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Deposito
from accounts.models import Transacao
from .models import Saque
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import Carteira

@login_required
def solicitar_deposito(request):
    if request.method == 'POST':
        try:
            valor_str = request.POST.get('valor').replace(',', '.') # Trata vírgula
            valor = float(valor_str)
            
            if valor >= 10.00:
                deposito = Deposito.objects.create(
                    usuario=request.user,
                    valor=valor
                )
                return redirect('pagamentos:pagar_pix', deposito_id=deposito.id)
            else:
                messages.error(request, "O valor mínimo para depósito é R$ 10,00.")
        except ValueError:
            messages.error(request, "Por favor, insira um valor numérico válido.")

    return render(request, 'pagamentos/solicitar_deposito.html')

@login_required
def pagar_pix(request, deposito_id):
    # Busca o depósito garantindo que pertence ao usuário logado
    deposito = get_object_or_404(Deposito, id=deposito_id, usuario=request.user)
    
    # Sua chave PIX real que vai aparecer na tela
    chave_pix = "fbd7d352-a8ec-4bda-8322-ea3ffaa08640" 

    context = {
        'deposito': deposito,
        'chave_pix': chave_pix
    }
    return render(request, 'pagamentos/pagar_pix.html', context)


@login_required
def extrato_carteira(request):
    # Busca a carteira do usuário atual
    carteira = request.user.carteira
    
    # Busca todas as transações vinculadas a essa carteira, ordenadas por data decrescente
    transacoes = Transacao.objects.filter(carteira=carteira).order_by('-data')
    
    context = {
        'carteira': carteira,
        'transacoes': transacoes
    }
    return render(request, 'pagamentos/extrato.html', context)


@login_required
def solicitar_saque(request):
    if request.method == 'POST':
        try:
            valor = Decimal(request.POST.get('valor').replace(',', '.'))
            chave_pix = request.POST.get('chave_pix')
            senha_confirmacao = request.POST.get('senha_confirmacao') # <--- NOVO
            carteira = request.user.carteira
            
            # --- TRAVA DE SEGURANÇA MÁXIMA ---
            # Verifica se a senha digitada bate com a senha do usuário logado
            if not request.user.check_password(senha_confirmacao):
                messages.error(request, "🛡️ Senha incorreta! Por segurança, a solicitação foi bloqueada.")
                return redirect('pagamentos:solicitar_saque')
            
            if valor < 10.00:
                messages.error(request, "O valor mínimo para saque é R$ 10,00.")
            elif valor > carteira.saldo:
                messages.error(request, f"Saldo insuficiente. Você tem R$ {carteira.saldo} disponível.")
            else:
                with transaction.atomic():
                    # Desconta o saldo IMEDIATAMENTE
                    carteira.saldo -= valor
                    carteira.save()
                    
                    Saque.objects.create(usuario=request.user, valor=valor, chave_pix=chave_pix)
                    
                    Transacao.objects.create(
                        carteira=carteira, tipo='saque', valor=valor,
                        descricao=f"Saque Solicitado (PIX: {chave_pix})"
                    )
                messages.success(request, "Saque solicitado com sucesso! Nossa equipe fará a transferência em breve.")
                return redirect('pagamentos:extrato')
        except Exception as e:
            messages.error(request, "Erro ao processar a solicitação. Verifique os valores.")

    return render(request, 'pagamentos/solicitar_saque.html')

@staff_member_required
def relatorio_gerencial(request):
    """ View protegida: Apenas Superusuários e Staff podem acessar """
    
    # 1. Total retido nas carteiras (Dinheiro dos jogadores)
    total_usuarios = Carteira.objects.aggregate(Sum('saldo'))['saldo__sum'] or Decimal('0.00')

    # 2. Matemática do Caixa do Sistema (Lucro da Casa)
    total_apostas = Transacao.objects.filter(tipo='aposta').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    total_premios = Transacao.objects.filter(tipo='premio').aggregate(Sum('valor'))['valor__sum'] or Decimal('0.00')
    lucro_sistema = total_apostas - total_premios # Aqui estão os seus 5% acumulados

    # 3. Saques pendentes (Para você não esquecer de pagar a galera)
    saques_pendentes = Saque.objects.filter(aprovado=False).count()

    # 4. Lista de todas as carteiras ordenadas por quem tem mais dinheiro
    carteiras = Carteira.objects.select_related('usuario').order_by('-saldo')

    # 5. As últimas 15 transações de TODO o sistema (Auditoria)
    # Obs: Usando '-id' para pegar as mais recentes caso não tenha um campo de data explícito na ordem
    ultimas_transacoes = Transacao.objects.all().order_by('-id')[:15] 

    context = {
        'total_usuarios': total_usuarios,
        'lucro_sistema': lucro_sistema,
        'saques_pendentes': saques_pendentes,
        'carteiras': carteiras,
        'ultimas_transacoes': ultimas_transacoes,
    }
    return render(request, 'pagamentos/relatorio_admin.html', context)
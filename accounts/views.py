from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegistroSimplesForm

# 1. IMPORTAMOS OS MODELS DE CARTEIRA E PARTICIPAÇÃO
from accounts.models import Carteira
from bolao.models import Participacao

def acesso_usuario(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form_login = AuthenticationForm()
    form_registro = RegistroSimplesForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            form_login = AuthenticationForm(request, data=request.POST)
            if form_login.is_valid():
                user = form_login.get_user()
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "E-mail ou senha incorretos.")

        elif action == 'registro':
            form_registro = RegistroSimplesForm(request.POST)
            if form_registro.is_valid():
                # Salva o usuário básico
                user = form_registro.save()
                
                # 2. MÁGICA AQUI: Cria automaticamente a Carteira e a Participação padrão
                Carteira.objects.get_or_create(usuario=user, defaults={'saldo': 0.00})
                Participacao.objects.get_or_create(usuario=user, defaults={'tipo': 'resenha', 'aprovado': True})
                
                # Faz o login automático
                login(request, user)
                messages.success(request, "Conta criada com sucesso! Bem-vindo(a) à Cartolândia.")
                return redirect('dashboard')
            else:
                messages.error(request, "Erro ao criar conta. Verifique os dados fornecidos.")

    context = {
        'form_login': form_login,
        'form_registro': form_registro
    }
    return render(request, 'accounts/login_registro.html', context)

def sair(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta. Até logo!")
    return redirect('login')
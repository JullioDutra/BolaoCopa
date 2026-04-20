from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Participacao


@login_required
def escolher_plano(request):
    # Se o usuário já tem uma participação criada, tira ele daqui
    if hasattr(request.user, 'participacao'):
        return redirect('dashboard') # <--- MUDOU AQUI (Tirou o 'core:')

    if request.method == 'POST':
        tipo_escolhido = request.POST.get('tipo_plano')
        
        if tipo_escolhido in ['resenha', 'pago']:
            Participacao.objects.create(
                usuario=request.user,
                tipo=tipo_escolhido
            )
            
            if tipo_escolhido == 'pago':
                return redirect('pagamentos:solicitar_deposito') 
            
            # Se for resenha, vai direto pro dashboard
            return redirect('dashboard') # <--- MUDOU AQUI (Tirou o 'core:')

    return render(request, 'bolao/escolher_plano.html')
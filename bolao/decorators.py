from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def acesso_liberado_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verifica se está logado
        if not request.user.is_authenticated:
            messages.error(request, "Você precisa fazer login para acessar o bolão.")
            return redirect('login')
            
        # Removemos a trava de aprovação global! 
        # Agora o usuário entra livre no painel e a cobrança ocorre só no botão que ele clicar.
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
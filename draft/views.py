from django.http import JsonResponse
import random
# Certifique-se de importar os models: from .models import ClubeBrasileiro, ElencoHistorico, JogadorDraft, SessaoDraft, EscolhaDraft

# ==========================================
# VIEWS DO DRAFT: COPA DO BRASIL HISTÓRICA
# ==========================================

@login_required
def iniciar_draft(request):
    """Cria uma nova prancheta zerada para o usuário começar o Draft."""
    # Por enquanto, vamos fixar o 4-3-3 para facilitar. Depois podemos deixar ele escolher.
    sessao = SessaoDraft.objects.create(
        usuario=request.user,
        formacao='4-3-3',
        status='montando'
    )
    return redirect('duelos:painel_draft', sessao_id=sessao.id)

@login_required
def painel_draft(request, sessao_id):
    """A tela principal onde o cara vê a prancheta e o botão de girar a roleta."""
    sessao = get_object_or_404(SessaoDraft, id=sessao_id, usuario=request.user)
    
    # Lista de posições que precisam ser preenchidas no 4-3-3
    posicoes_taticas = [
        'Goleiro', 'Lateral Direito', 'Zagueiro 1', 'Zagueiro 2', 'Lateral Esquerdo',
        'Volante', 'Meia Direita', 'Meia Esquerda', 'Ponta Direita', 'Ponta Esquerda', 'Centroavante'
    ]
    
    # Pega os jogadores que ele já puxou pra prancheta
    escolhas_feitas = sessao.escolhas.all()
    posicoes_preenchidas = [escolha.posicao_escalada for escolha in escolhas_feitas]
    
    return render(request, 'duelos/painel_draft.html', {
        'sessao': sessao,
        'posicoes_taticas': posicoes_taticas,
        'escolhas': escolhas_feitas,
        'posicoes_preenchidas': posicoes_preenchidas
    })

@login_required
def sortear_elenco_api(request, sessao_id):
    """A roleta mágica. Sorteia um time do passado e devolve as cartas dos jogadores."""
    sessao = get_object_or_404(SessaoDraft, id=sessao_id, usuario=request.user)
    
    if sessao.status != 'montando':
        return JsonResponse({'erro': 'Draft fechado! Você já montou seu time.'}, status=400)
        
    # Pega todos os elencos que você cadastrou no banco
    elencos_ids = list(ElencoHistorico.objects.values_list('id', flat=True))
    
    if not elencos_ids:
        return JsonResponse({'erro': 'O VAR informa: Nenhum time histórico cadastrado no sistema ainda!'}, status=400)
        
    # Sorteia um elenco (Ex: Sorteou o ID do Cruzeiro 2003)
    elenco_sorteado_id = random.choice(elencos_ids)
    elenco = ElencoHistorico.objects.get(id=elenco_sorteado_id)
    
    # Busca todas as cartas de jogadores desse elenco
    jogadores = elenco.jogadores.all()
    
    # Monta a resposta que vai para a tela animar e mostrar as cartas
    jogadores_data = []
    for j in jogadores:
        jogadores_data.append({
            'id': j.id,
            'nome': j.nome,
            'posicao': j.get_posicao_display(),
            'nota': j.nota_geral,
            'foto': j.foto.url if j.foto else 'https://i.pravatar.cc/150?img=11' # Foto coringa se não tiver
        })
        
    return JsonResponse({
        'clube': elenco.clube.nome,
        'ano': elenco.ano,
        'escudo': elenco.clube.escudo.url if elenco.clube.escudo else '',
        'jogadores': jogadores_data
    })
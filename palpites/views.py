from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q, Max
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ResultadosFinaisForm, PalpiteLongoPrazoForm
from .engine import processar_pontuacoes_longo_prazo
from .models import PalpiteLongoPrazo, Temporada


# Imports dos seus aplicativos
from bolao.decorators import acesso_liberado_required
from .models import Jogo, Palpite, OscarCartolandia
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




# Mantenha os seus outros imports aqui (ex: @acesso_liberado_required, Palpite, etc.)

@acesso_liberado_required
def ranking_geral(request):
    """ Soma a pontuação de todos os palpites agrupando por usuário e monta a tabela do ranking """
    
    ranking = Palpite.objects.values(
        'usuario__username', 
        'usuario__first_name', 
        'usuario__participacao__tipo'
    ).annotate(
        # Soma total dos pontos
        total_pontos=Sum('pontuacao_obtida'),
        
        # Conta quantos palpites o usuário tem com pontuação igual a 15
        acertos_placar=Count('id', filter=Q(pontuacao_obtida=15)),
        
        # Conta quantos palpites o usuário tem com pontuação igual a 5
        # NOTA: Veja a observação abaixo sobre o Maior Pontuador
        acertos_vencedor=Count('id', filter=Q(pontuacao_obtida=5)),
        
        # Se você criou um campo booleano no model Palpite chamado 'is_maior_pontuador',
        # você poderia contar assim:
        maior_pontuador=Count('id', filter=Q(is_maior_pontuador=True)),
        
    ).order_by('-total_pontos')
        
    return render(request, 'palpites/ranking.html', {'ranking': ranking})


@login_required
def indicar_oscar(request):
    if request.method == 'POST':
        categoria = request.POST.get('categoria')
        autor = request.POST.get('autor')
        fala = request.POST.get('fala')
        nivel = request.POST.get('nivel')
        print_prova = request.FILES.get('print_prova') # Pega a imagem se tiver

        # Salva a fofoca no banco
        OscarCartolandia.objects.create(
            indicado_por=request.user,
            categoria=categoria,
            autor=autor,
            fala=fala,
            nivel=nivel,
            print_prova=print_prova
        )
        
        messages.success(request, "Indicação registrada com sucesso! O VAR já tem as provas.")
        return redirect('palpites:indicar_oscar') # Recarrega a página limpando o form

    return render(request, 'palpites/indicar_oscar.html')



@staff_member_required
def inserir_resultados_finais(request):
    if request.method == 'POST':
        form = ResultadosFinaisForm(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            temporada_ano = dados['temporada_ano'].ano
            
            # Monta o dicionário de classificação do Brasileirão
            classificacao_br = {
                1: dados['campeao_br'].id,
                2: dados['vice_br'].id,
                3: dados['terceiro_br'].id,
                4: dados['quarto_br'].id,
                17: dados['pos_17'].id,
                18: dados['pos_18'].id,
                19: dados['pos_19'].id,
                20: dados['pos_20'].id,
            }
            
            id_europa = dados['campeao_europa'].id
            id_cdb = dados['campeao_cdb'].id
            
            # Dispara a Engine
            sucesso = processar_pontuacoes_longo_prazo(
                temporada_ano=temporada_ano,
                classificacao_br=classificacao_br,
                id_campeao_europa=id_europa,
                id_campeao_cdb=id_cdb
            )
            
            if sucesso:
                messages.success(request, "Resultados processados e pontos distribuídos com sucesso! Agora você já pode finalizar a temporada no Admin.")
            else:
                messages.error(request, "Erro ao processar. Verifique se a temporada está ativa.")
                
            return redirect('inserir_resultados_finais')
    else:
        form = ResultadosFinaisForm()
        
    return render(request, 'palpites/inserir_resultados.html', {'form': form})

@login_required
def meus_palpites_longo_prazo(request):
    temporada = Temporada.objects.filter(ativa=True).first()
    if not temporada:
        messages.error(request, "Nenhuma temporada ativa no momento.")
        return redirect('dashboard') # Ou o nome da sua home
        
    if request.method == 'POST':
        form = PalpiteLongoPrazoForm(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            
            # Mapeamento para salvar no formato correto do banco
            mapeamento = [
                ('CAMPEAO_BR', 1, dados['campeao_br']),
                ('G4', 2, dados['g4_2']),
                ('G4', 3, dados['g4_3']),
                ('G4', 4, dados['g4_4']),
                ('Z4', 17, dados['z4_17']),
                ('Z4', 18, dados['z4_18']),
                ('Z4', 19, dados['z4_19']),
                ('Z4', 20, dados['z4_20']),
                ('CAMPEAO_EUROPA', 1, dados['campeao_europa']),
                ('CAMPEAO_CDB', 1, dados['campeao_cdb']),
            ]
            
            with transaction.atomic():
                # Deleta os antigos desta temporada para o usuário e recria
                PalpiteLongoPrazo.objects.filter(usuario=request.user, temporada=temporada).delete()
                
                for tipo, pos, clube in mapeamento:
                    if clube: 
                        PalpiteLongoPrazo.objects.create(
                            usuario=request.user,
                            temporada=temporada,
                            tipo=tipo,
                            posicao_esperada=pos,
                            clube=clube
                        )
            messages.success(request, "Seus palpites foram salvos com sucesso!")
            return redirect('meus_palpites_longo_prazo')
    else:
        # Preenche o formulário se o usuário já tiver apostado
        palpites_existentes = PalpiteLongoPrazo.objects.filter(usuario=request.user, temporada=temporada)
        iniciais = {}
        for p in palpites_existentes:
            if p.tipo == 'CAMPEAO_BR': iniciais['campeao_br'] = p.clube
            elif p.tipo == 'CAMPEAO_EUROPA': iniciais['campeao_europa'] = p.clube
            elif p.tipo == 'CAMPEAO_CDB': iniciais['campeao_cdb'] = p.clube
            elif p.tipo == 'G4': iniciais[f'g4_{p.posicao_esperada}'] = p.clube
            elif p.tipo == 'Z4': iniciais[f'z4_{p.posicao_esperada}'] = p.clube
        
        form = PalpiteLongoPrazoForm(initial=iniciais)
        
    # Busca os palpites salvos para exibir os cards
    palpites_salvos = PalpiteLongoPrazo.objects.filter(usuario=request.user, temporada=temporada).order_by('posicao_esperada')
    
    return render(request, 'palpites/meus_palpites_longo_prazo.html', {
        'form': form,
        'palpites_salvos': palpites_salvos,
        'temporada': temporada
    })

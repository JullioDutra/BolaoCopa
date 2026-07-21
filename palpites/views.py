from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Max, Count
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .forms import ResultadosFinaisForm, PalpiteLongoPrazoForm, PalpiteForm
from .engine import processar_pontuacoes_longo_prazo
from .models import Jogo, Palpite, OscarCartolandia, PalpiteLongoPrazo, Temporada, MuralCampeoes, Clube
from .ranking_utils import calcular_ranking_geral

from bolao.decorators import acesso_liberado_required
from accounts.models import Transacao


@acesso_liberado_required
def listar_jogos(request):
    jogos = Jogo.objects.all().order_by('data_hora')
    meus_palpites = Palpite.objects.filter(usuario=request.user)
    palpites_dict = {palpite.jogo.id: palpite for palpite in meus_palpites}

    for jogo in jogos:
        jogo.meu_palpite = palpites_dict.get(jogo.id)
        if jogo.finalizado and jogo.premio_distribuido:
            maior_pontuacao = Palpite.objects.filter(jogo=jogo, modalidade='pago').aggregate(Max('pontuacao_obtida'))['pontuacao_obtida__max']
            if maior_pontuacao is not None and maior_pontuacao > 0:
                jogo.ganhadores = Palpite.objects.filter(jogo=jogo, modalidade='pago', pontuacao_obtida=maior_pontuacao)
            else:
                jogo.ganhadores = []

    jogadores_pago = User.objects.filter(palpites__modalidade='pago').distinct()
    jogadores_resenha = User.objects.filter(palpites__modalidade='resenha').exclude(id__in=jogadores_pago).distinct()

    return render(request, 'palpites/listar_jogos.html', {
        'jogos': jogos,
        'jogadores_pago': jogadores_pago,
        'jogadores_resenha': jogadores_resenha
    })


@acesso_liberado_required
def fazer_palpite(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)

    if not jogo.aceita_palpite:
        messages.error(request, "Este jogo não aceita mais palpites. O prazo encerrou!")
        return redirect('palpites:listar_jogos')

    palpite_existente = Palpite.objects.filter(usuario=request.user, jogo=jogo).first()

    if request.method == 'POST':
        form = PalpiteForm(request.POST, instance=palpite_existente, jogo=jogo)
        tipo_aposta = request.POST.get('tipo_aposta', 'resenha')

        if form.is_valid():
            palpite = form.save(commit=False)
            palpite.usuario = request.user
            palpite.jogo = jogo

            ja_era_pago = palpite_existente and palpite_existente.modalidade == 'pago'

            if tipo_aposta == 'pago' and not ja_era_pago:
                custo = Decimal('10.00')
                if request.user.carteira.saldo < custo:
                    messages.error(request, "Saldo insuficiente! Deposite R$ 10,00 ou jogue no Modo Resenha.")
                    return redirect('pagamentos:solicitar_deposito')

                with transaction.atomic():
                    request.user.carteira.saldo -= custo
                    request.user.carteira.save()
                    Transacao.objects.create(
                        carteira=request.user.carteira,
                        tipo='aposta',
                        valor=custo,
                        descricao=f"Palpite Valendo Prêmio: {jogo.time_casa} x {jogo.time_fora}"
                    )
                    palpite.modalidade = 'pago'
                    palpite.save()

                messages.success(request, "Palpite registrado Valendo Prêmio! (R$ 10,00 descontados)")
            else:
                if not ja_era_pago:
                    palpite.modalidade = 'resenha'
                palpite.save()

                if palpite_existente:
                    messages.success(request, "Seu palpite foi atualizado com sucesso!")
                else:
                    messages.success(request, "Palpite salvo na Resenha!")

            return redirect('palpites:listar_jogos')
    else:
        form = PalpiteForm(instance=palpite_existente)

    return render(request, 'palpites/fazer_palpite.html', {
        'form': form,
        'jogo': jogo,
        'palpite_existente': palpite_existente
    })


@acesso_liberado_required
def ranking_geral(request):
    """ Ranking geral combinando: jogos do Bolão + Longo Prazo (Campeão/G4/Z4/Europa/CDB) + Seleção 4-3-3 """
    temporada_ativa = Temporada.objects.filter(ativa=True).first()
    ranking = calcular_ranking_geral(temporada=temporada_ativa)
    return render(request, 'palpites/ranking.html', {
        'ranking': ranking,
        'temporada_ativa': temporada_ativa,
    })


@login_required
def indicar_oscar(request):
    if request.method == 'POST':
        categoria = request.POST.get('categoria')
        autor = request.POST.get('autor')
        fala = request.POST.get('fala')
        nivel = request.POST.get('nivel')
        print_prova = request.FILES.get('print_prova')

        OscarCartolandia.objects.create(
            indicado_por=request.user,
            categoria=categoria,
            autor=autor,
            fala=fala,
            nivel=nivel,
            print_prova=print_prova
        )

        messages.success(request, "Indicação registrada com sucesso! O VAR já tem as provas.")
        return redirect('palpites:indicar_oscar')

    return render(request, 'palpites/indicar_oscar.html')


@staff_member_required
def inserir_resultados_finais(request):
    if request.method == 'POST':
        form = ResultadosFinaisForm(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            temporada_ano = dados['temporada_ano'].ano

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

            return redirect('palpites:inserir_resultados_finais')
    else:
        form = ResultadosFinaisForm()

    return render(request, 'palpites/inserir_resultados.html', {'form': form, 'clubes': Clube.objects.all()})


@login_required
def meus_palpites_longo_prazo(request):
    temporada = Temporada.objects.filter(ativa=True).first()
    if not temporada:
        messages.error(request, "Nenhuma temporada ativa no momento.")
        return redirect('dashboard')

    if request.method == 'POST':
        # Passa a temporada para o form aplicar as regras de bloqueio
        form = PalpiteLongoPrazoForm(request.POST, temporada=temporada)
        
        if form.is_valid():
            dados = form.cleaned_data

            with transaction.atomic():
                # 1. PROCESSAR BRASILEIRÃO (Apenas se o prazo permitir)
                if temporada.brasileirao_aberto():
                    # Deleta os antigos do Brasileirão para recriar
                    PalpiteLongoPrazo.objects.filter(
                        usuario=request.user, 
                        temporada=temporada, 
                        tipo__in=['CAMPEAO_BR', 'G4', 'Z4']
                    ).delete()
                    
                    mapeamento_br = [
                        ('CAMPEAO_BR', 1, dados.get('campeao_br')),
                        ('G4', 2, dados.get('g4_2')),
                        ('G4', 3, dados.get('g4_3')),
                        ('G4', 4, dados.get('g4_4')),
                        ('Z4', 17, dados.get('z4_17')),
                        ('Z4', 18, dados.get('z4_18')),
                        ('Z4', 19, dados.get('z4_19')),
                        ('Z4', 20, dados.get('z4_20')),
                    ]
                    for tipo, pos, clube in mapeamento_br:
                        if clube:
                            PalpiteLongoPrazo.objects.create(
                                usuario=request.user, 
                                temporada=temporada, 
                                tipo=tipo, 
                                posicao_esperada=pos, 
                                clube=clube
                            )

                # 2. PROCESSAR COPAS FIXAS (Apenas se o prazo permitir)
                if temporada.copas_fixas_abertas():
                    PalpiteLongoPrazo.objects.filter(
                        usuario=request.user, 
                        temporada=temporada, 
                        tipo__in=['CAMPEAO_EUROPA', 'CAMPEAO_CDB']
                    ).delete()
                    
                    mapeamento_copas = [
                        ('CAMPEAO_EUROPA', 1, dados.get('campeao_europa')),
                        ('CAMPEAO_CDB', 1, dados.get('campeao_cdb')),
                    ]
                    for tipo, pos, clube in mapeamento_copas:
                        if clube:
                            PalpiteLongoPrazo.objects.create(
                                usuario=request.user, 
                                temporada=temporada, 
                                tipo=tipo, 
                                posicao_esperada=pos, 
                                clube=clube
                            )

                # 3. PROCESSAR TORNEIOS DINÂMICOS EXTRAS
                for torneio in temporada.torneios_extras.all():
                    if torneio.is_aberto():
                        nome_campo = f'torneio_extra_{torneio.id}'
                        clube_escolhido = dados.get(nome_campo)
                        
                        if clube_escolhido:
                            PalpiteTorneioExtra.objects.update_or_create(
                                usuario=request.user,
                                torneio=torneio,
                                defaults={'clube': clube_escolhido}
                            )
                        else:
                            # Se o usuário limpou o select, excluímos o palpite
                            PalpiteTorneioExtra.objects.filter(usuario=request.user, torneio=torneio).delete()

            messages.success(request, "Seus palpites foram processados e salvos!")
            return redirect('palpites:meus_palpites_longo_prazo')

    else:
        iniciais = {}
        
        # Puxa os dados iniciais dos torneios fixos
        palpites_existentes = PalpiteLongoPrazo.objects.filter(usuario=request.user, temporada=temporada)
        for p in palpites_existentes:
            if p.tipo == 'CAMPEAO_BR': iniciais['campeao_br'] = p.clube
            elif p.tipo == 'CAMPEAO_EUROPA': iniciais['campeao_europa'] = p.clube
            elif p.tipo == 'CAMPEAO_CDB': iniciais['campeao_cdb'] = p.clube
            elif p.tipo == 'G4': iniciais[f'g4_{p.posicao_esperada}'] = p.clube
            elif p.tipo == 'Z4': iniciais[f'z4_{p.posicao_esperada}'] = p.clube

        # Puxa os dados iniciais dos torneios extras
        palpites_extras = PalpiteTorneioExtra.objects.filter(usuario=request.user, torneio__temporada=temporada)
        for p_extra in palpites_extras:
            iniciais[f'torneio_extra_{p_extra.torneio.id}'] = p_extra.clube

        form = PalpiteLongoPrazoForm(initial=iniciais, temporada=temporada)

    # Recupera os palpites já salvos para exibição nos cards da parte inferior da tela
    palpites_salvos = PalpiteLongoPrazo.objects.filter(usuario=request.user, temporada=temporada).order_by('posicao_esperada')
    palpites_extras_salvos = PalpiteTorneioExtra.objects.filter(usuario=request.user, torneio__temporada=temporada)
    
    mais_votados = _calcular_mais_votados(temporada)

    return render(request, 'palpites/meus_palpites_longo_prazo.html', {
        'form': form,
        'palpites_salvos': palpites_salvos,
        'palpites_extras_salvos': palpites_extras_salvos, # Passa os palpites dinâmicos separados
        'temporada': temporada,
        'clubes': Clube.objects.all(),
        'mais_votados': mais_votados,
    })


def _calcular_mais_votados(temporada):
    """
    Retorna, para cada posição/categoria de palpite de longo prazo, o clube
    mais indicado pelos usuários e quantos votos (palpites) ele recebeu.
    Usado para montar o painel "Favoritos da Torcida".
    """
    if not temporada:
        return []
 
    contagem = (
        PalpiteLongoPrazo.objects
        .filter(temporada=temporada)
        .values('tipo', 'posicao_esperada', 'clube_id')
        .annotate(total=Count('id'))
        .order_by('tipo', 'posicao_esperada', '-total')
    )
 
    top_por_categoria = {}
    total_votantes = {}
    for item in contagem:
        chave = (item['tipo'], item['posicao_esperada'])
        total_votantes[chave] = total_votantes.get(chave, 0) + item['total']
        # A query já vem ordenada por -total dentro de cada categoria,
        # então o primeiro registro encontrado é o mais votado.
        if chave not in top_por_categoria:
            top_por_categoria[chave] = item
 
    clube_ids = [v['clube_id'] for v in top_por_categoria.values()]
    clubes_map = {c.id: c for c in Clube.objects.filter(id__in=clube_ids)}
 
    # Define a ordem de exibição e os textos/ícones de cada categoria
    ORDEM = [
        ('CAMPEAO_BR', 1, 'Campeão Brasileiro', 'fa-trophy', 'text-warning'),
        ('G4', 2, 'G4 · 2º Lugar', 'fa-medal', 'text-warning'),
        ('G4', 3, 'G4 · 3º Lugar', 'fa-medal', 'text-warning'),
        ('G4', 4, 'G4 · 4º Lugar', 'fa-medal', 'text-warning'),
        ('Z4', 17, 'Z4 · 17º Lugar', 'fa-arrow-down', 'text-danger'),
        ('Z4', 18, 'Z4 · 18º Lugar', 'fa-arrow-down', 'text-danger'),
        ('Z4', 19, 'Z4 · 19º Lugar', 'fa-arrow-down', 'text-danger'),
        ('Z4', 20, 'Z4 · 20º Lugar', 'fa-arrow-down', 'text-danger'),
        ('CAMPEAO_EUROPA', 1, 'Campeão Europa', 'fa-earth-europe', 'text-primary'),
        ('CAMPEAO_CDB', 1, 'Campeão Copa do Brasil', 'fa-shield-halved', 'text-primary'),
    ]
 
    resultado = []
    for tipo, pos, label, icone, cor_classe in ORDEM:
        chave = (tipo, pos)
        item = top_por_categoria.get(chave)
        if not item:
            continue
        clube = clubes_map.get(item['clube_id'])
        if not clube:
            continue
        total_geral = total_votantes.get(chave, 0)
        percentual = round((item['total'] / total_geral) * 100) if total_geral else 0
        resultado.append({
            'label': label,
            'icone': icone,
            'cor_classe': cor_classe,
            'clube': clube,
            'votos': item['total'],
            'total_votantes': total_geral,
            'percentual': percentual,
        })
 
    return resultado

@staff_member_required
def painel_controle_admin(request):
    """Painel de controle customizado para a staff gerenciar a temporada, resultados e zerar pontuações se necessário."""
    temporada_ativa = Temporada.objects.filter(ativa=True).first()
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'zerar_ranking':
            # Exemplo de ação para limpar dados de palpites de jogos ou longo prazo se necessário
            # (ajuste conforme a regra do seu engine/banco)
            messages.warning(request, "Ação de zerar ranking solicitada. Implemente a regra de limpeza desejada.")
            return redirect('palpites:painel_controle_admin')
            
        messages.success(request, "Ação executada com sucesso!")
        return redirect('palpites:painel_controle_admin')

    return render(request, 'palpites/painel_controle.html', {
        'temporada_ativa': temporada_ativa,
    })

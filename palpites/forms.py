from django import forms
from .models import Clube, Temporada, Palpite, Jogo


class PalpiteForm(forms.ModelForm):
    class Meta:
        model = Palpite
        fields = ['gols_casa', 'gols_fora']
        widgets = {
            'gols_casa': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'max': 20}),
            'gols_fora': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'max': 20}),
        }

    def __init__(self, *args, **kwargs):
        self.jogo = kwargs.pop('jogo', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.jogo and not self.jogo.aceita_palpite:
            raise forms.ValidationError("Tempo esgotado! A bola já rolou e os palpites para este jogo estão encerrados.")
        return cleaned_data


class ResultadosFinaisForm(forms.Form):
    temporada_ano = forms.ModelChoiceField(
        queryset=Temporada.objects.filter(ativa=True),
        label="Temporada Ativa",
        empty_label="Selecione a Temporada"
    )

    # G4 (só clubes do Brasileirão)
    campeao_br = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="1º Lugar (Campeão BR)")
    vice_br = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="2º Lugar")
    terceiro_br = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="3º Lugar")
    quarto_br = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="4º Lugar")

    # Z4 (só clubes do Brasileirão)
    pos_17 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="17º Lugar")
    pos_18 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="18º Lugar")
    pos_19 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="19º Lugar")
    pos_20 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="20º Lugar")

    # Outros Campeões
    campeao_europa = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='EUROPA'), label="Campeão Europeu (Champions)")
    campeao_cdb = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="Campeão Copa do Brasil")


class PalpiteLongoPrazoForm(forms.Form):
    campeao_br = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="Campeão", empty_label="Selecione o Clube")
    g4_2 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="2º Lugar", empty_label="Selecione o Clube")
    g4_3 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="3º Lugar", empty_label="Selecione o Clube")
    g4_4 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="4º Lugar", empty_label="Selecione o Clube")
    
    z4_17 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="17º Lugar", empty_label="Selecione o Clube")
    z4_18 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="18º Lugar", empty_label="Selecione o Clube")
    z4_19 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="19º Lugar", empty_label="Selecione o Clube")
    z4_20 = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="20º Lugar", empty_label="Selecione o Clube")
    
    campeao_europa = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="Champions League", empty_label="Selecione o Clube")
    campeao_cdb = forms.ModelChoiceField(queryset=Clube.objects.all(), required=False, label="Copa do Brasil", empty_label="Selecione o Clube")

    def __init__(self, *args, **kwargs):
        # Extrai a temporada dos kwargs antes de iniciar o form
        self.temporada = kwargs.pop('temporada', None)
        super().__init__(*args, **kwargs)

        if self.temporada:
            # 1. BLOQUEIO: Brasileirão (Campeão, G4, Z4)
            if not self.temporada.brasileirao_aberto():
                campos_br = ['campeao_br', 'g4_2', 'g4_3', 'g4_4', 'z4_17', 'z4_18', 'z4_19', 'z4_20']
                for campo in campos_br:
                    self.fields[campo].disabled = True
                    # Opcional: Adicionar uma classe CSS para deixar visualmente bloqueado
                    self.fields[campo].widget.attrs['class'] = 'bg-light text-muted' 

            # 2. BLOQUEIO: Copas Fixas
            if not self.temporada.copas_fixas_abertas():
                campos_copas = ['campeao_europa', 'campeao_cdb']
                for campo in campos_copas:
                    self.fields[campo].disabled = True
                    self.fields[campo].widget.attrs['class'] = 'bg-light text-muted'

            # 3. GERAÇÃO DINÂMICA: Torneios Extras
            for torneio in self.temporada.torneios_extras.all():
                nome_campo = f'torneio_extra_{torneio.id}'
                
                # Verifica se este torneio específico já fechou
                is_aberto = torneio.is_aberto()
                
                self.fields[nome_campo] = forms.ModelChoiceField(
                    queryset=Clube.objects.all(),
                    label=torneio.nome,
                    required=False,
                    disabled=not is_aberto,
                    empty_label="Selecione o Clube"
                )
                
                if not is_aberto:
                    self.fields[nome_campo].widget.attrs['class'] = 'bg-light text-muted'

class JogoAdminForm(forms.ModelForm):
    class Meta:
        model = Jogo
        # Removemos 'rodada' e 'aceita_palpite' da lista
        fields = ['time_casa', 'time_fora', 'data_hora', 'finalizado', 'premio_distribuido'] 
        widgets = {
            'data_hora': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

class TemporadaPrazoForm(forms.ModelForm):
    class Meta:
        model = Temporada
        # Atualizado para prazo_copas_fixas
        fields = ['prazo_brasileirao', 'prazo_copas_fixas'] 
        widgets = {
            'prazo_brasileirao': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            # Atualizado para prazo_copas_fixas
            'prazo_copas_fixas': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

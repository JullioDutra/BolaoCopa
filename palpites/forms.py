from django import forms
from .models import Clube, Temporada, Palpite


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
    # Campeão e G4 (só clubes do Brasileirão)
    campeao_br = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="1º Lugar (Campeão BR)")
    g4_2 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="2º Lugar (G4)")
    g4_3 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="3º Lugar (G4)")
    g4_4 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="4º Lugar (G4)")

    # Z4 (só clubes do Brasileirão)
    z4_17 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="17º Lugar (Z4)")
    z4_18 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="18º Lugar (Z4)")
    z4_19 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="19º Lugar (Z4)")
    z4_20 = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="20º Lugar (Z4)")

    # Outros Torneios
    campeao_europa = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='EUROPA'), label="Campeão Europeu (Champions)")
    campeao_cdb = forms.ModelChoiceField(queryset=Clube.objects.filter(competicao='BRASILEIRAO'), label="Campeão Copa do Brasil")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

from django import forms
from .models import Clube, Temporada,Palpite

class PalpiteForm(forms.ModelForm):
    class Meta:
        model = Palpite
        fields = ['gols_casa', 'gols_fora']
        widgets = {
            'gols_casa': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'max': 20}),
            'gols_fora': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'max': 20}),
        }

    def __init__(self, *args, **kwargs):
        # Capturamos o jogo que a View vai enviar
        self.jogo = kwargs.pop('jogo', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        
        # Ponto Crítico: Trava se o jogo já começou
        if self.jogo and not self.jogo.aceita_palpite:
            raise forms.ValidationError("Tempo esgotado! A bola já rolou e os palpites para este jogo estão encerrados.")
            
        return cleaned_data


class ResultadosFinaisForm(forms.Form):
    temporada_ano = forms.ModelChoiceField(
        queryset=Temporada.objects.filter(ativa=True),
        label="Temporada Ativa",
        empty_label="Selecione a Temporada"
    )
    
    # G4
    campeao_br = forms.ModelChoiceField(queryset=Clube.objects.all(), label="1º Lugar (Campeão BR)")
    vice_br = forms.ModelChoiceField(queryset=Clube.objects.all(), label="2º Lugar")
    terceiro_br = forms.ModelChoiceField(queryset=Clube.objects.all(), label="3º Lugar")
    quarto_br = forms.ModelChoiceField(queryset=Clube.objects.all(), label="4º Lugar")
    
    # Z4
    pos_17 = forms.ModelChoiceField(queryset=Clube.objects.all(), label="17º Lugar")
    pos_18 = forms.ModelChoiceField(queryset=Clube.objects.all(), label="18º Lugar")
    pos_19 = forms.ModelChoiceField(queryset=Clube.objects.all(), label="19º Lugar")
    pos_20 = forms.ModelChoiceField(queryset=Clube.objects.all(), label="20º Lugar")
    
    # Outros Campeões
    campeao_europa = forms.ModelChoiceField(queryset=Clube.objects.all(), label="Campeão Europeu (Champions)")
    campeao_cdb = forms.ModelChoiceField(queryset=Clube.objects.all(), label="Campeão Copa do Brasil")

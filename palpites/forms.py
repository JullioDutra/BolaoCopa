from django import forms
from .models import Palpite

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
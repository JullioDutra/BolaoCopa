from django import forms
from .models import Convocacao

class ConvocacaoForm(forms.ModelForm):
    class Meta:
        model = Convocacao
        fields = ['jogadores']
        # Usamos um CheckboxSelectMultiple para facilitar a interface depois
        widgets = {
            'jogadores': forms.CheckboxSelectMultiple()
        }

    def clean_jogadores(self):
        """
        Essa função 'clean' é executada pelo Django para validar o campo.
        É aqui que colocamos a nossa trava inquebrável.
        """
        jogadores = self.cleaned_data.get('jogadores')
        
        # Ponto Crítico de Segurança: Trava de 26 nomes
        if jogadores.count() != 26:
            raise forms.ValidationError(f"Você deve convocar exatamente 26 jogadores! Você selecionou {jogadores.count()}.")
            
        return jogadores
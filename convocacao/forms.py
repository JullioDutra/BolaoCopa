from django import forms
from .models import Convocacao, Jogador

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


class SelecaoBrasileiraoForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra os jogadores por posição para carregar nos selects
        goleiros = Jogador.objects.filter(posicao='Goleiro')
        defensores = Jogador.objects.filter(posicao='Defensor')
        meias = Jogador.objects.filter(posicao='Meio-campista')
        atacantes = Jogador.objects.filter(posicao='Atacante')

        # Goleiro (1)
        self.fields['goleiro'] = forms.ModelChoiceField(
            queryset=goleiros, empty_label="Escalar Goleiro"
        )
        
        # Defensores (4)
        for i in range(1, 5):
            self.fields[f'defensor_{i}'] = forms.ModelChoiceField(
                queryset=defensores, empty_label=f"Escalar ZAG/LAT"
            )
        
        # Meio-campistas (3)
        for i in range(1, 4):
            self.fields[f'meia_{i}'] = forms.ModelChoiceField(
                queryset=meias, empty_label=f"Escalar MEI"
            )
        
        # Atacantes (3)
        for i in range(1, 4):
            self.fields[f'atacante_{i}'] = forms.ModelChoiceField(
                queryset=atacantes, empty_label=f"Escalar ATA"
            )

        # Adiciona a classe CSS padronizada para os selects
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-select form-select-sm selecao-input'})

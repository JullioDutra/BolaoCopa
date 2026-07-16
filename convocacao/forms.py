from django import forms
from .models import Convocacao, Jogador, SelecaoBrasileirao


class ConvocacaoForm(forms.ModelForm):
    """Mantido apenas para referência histórica do modo Copa (encerrado)."""
    class Meta:
        model = Convocacao
        fields = ['jogadores']
        widgets = {
            'jogadores': forms.CheckboxSelectMultiple()
        }

    def clean_jogadores(self):
        jogadores = self.cleaned_data.get('jogadores')
        if jogadores.count() != 26:
            raise forms.ValidationError(f"Você deve convocar exatamente 26 jogadores! Você selecionou {jogadores.count()}.")
        return jogadores


class SelecaoBrasileiraoForm(forms.ModelForm):
    """Formulário do novo modo: escalação 4-3-3 do Brasileirão."""

    class Meta:
        model = SelecaoBrasileirao
        fields = [
            'goleiro',
            'defensor_1', 'defensor_2', 'defensor_3', 'defensor_4',
            'meia_1', 'meia_2', 'meia_3',
            'atacante_1', 'atacante_2', 'atacante_3',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        goleiros = Jogador.objects.filter(posicao='Goleiro')
        defensores = Jogador.objects.filter(posicao='Defensor')
        meias = Jogador.objects.filter(posicao='Meio-campista')
        atacantes = Jogador.objects.filter(posicao='Atacante')

        self.fields['goleiro'].queryset = goleiros
        self.fields['goleiro'].empty_label = "Escalar Goleiro"

        for i in range(1, 5):
            self.fields[f'defensor_{i}'].queryset = defensores
            self.fields[f'defensor_{i}'].empty_label = "Escalar ZAG/LAT"

        for i in range(1, 4):
            self.fields[f'meia_{i}'].queryset = meias
            self.fields[f'meia_{i}'].empty_label = "Escalar MEI"
            self.fields[f'atacante_{i}'].queryset = atacantes
            self.fields[f'atacante_{i}'].empty_label = "Escalar ATA"

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-select form-select-sm selecao-input'})

    def clean(self):
        cleaned_data = super().clean()
        campos = [
            'goleiro', 'defensor_1', 'defensor_2', 'defensor_3', 'defensor_4',
            'meia_1', 'meia_2', 'meia_3', 'atacante_1', 'atacante_2', 'atacante_3',
        ]
        selecionados = [cleaned_data.get(c) for c in campos if cleaned_data.get(c)]
        ids = [j.id for j in selecionados]
        if len(ids) == len(campos) and len(set(ids)) != len(campos):
            raise forms.ValidationError("Você não pode escalar o mesmo jogador em mais de uma posição.")
        return cleaned_data

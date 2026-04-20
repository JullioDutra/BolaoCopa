from django import forms

class DepositoForm(forms.Form):
    valor = forms.DecimalField(
        min_value=10.00, 
        max_digits=10, 
        decimal_places=2,
        label="Valor para Adicionar",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo R$ 10,00'})
    )
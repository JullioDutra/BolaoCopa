from django import forms
from django.contrib.auth.models import User

class RegistroSimplesForm(forms.ModelForm):
    nome = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Como devemos te chamar?'})
    )
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'seu@email.com'})
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Crie uma senha segura'})
    )

    class Meta:
        model = User
        fields = ['nome', 'email', 'senha']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso. Tente fazer login.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # O Django exige um username, então usamos o email
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['nome']
        user.email = self.cleaned_data['email']
        user.set_password(self.cleaned_data['senha']) # Criptografa a senha com segurança
        if commit:
            user.save()
        return user
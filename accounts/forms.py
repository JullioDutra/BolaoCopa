from django import forms
from django.contrib.auth.models import User

from . import dados
from .models import PerfilUsuario

from . import avatares as _avatares

CLASSE = 'form-control form-control-lg'


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
    whatsapp = forms.CharField(
        required=False, max_length=25, label='WhatsApp',
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'WhatsApp (opcional) — ajuda a recuperar a senha',
                                      'inputmode': 'tel', 'autocomplete': 'tel'})
    )

    class Meta:
        model = User
        fields = ['nome', 'email', 'senha']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError("Este e-mail já está em uso. Tente fazer login.")
        return email

    def clean_whatsapp(self):
        try:
            return dados.normalizar_telefone(self.cleaned_data.get('whatsapp'))
        except ValueError as erro:
            raise forms.ValidationError(str(erro))

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


class PerfilForm(forms.Form):
    """ Dados básicos que o participante pode mudar. """
    nome = forms.CharField(max_length=100, label='Como te chamam', widget=forms.TextInput(attrs={'class': CLASSE}))
    email = forms.EmailField(label='E-mail (usado no login)', widget=forms.EmailInput(attrs={'class': CLASSE}))
    telefone = forms.CharField(required=False, max_length=25, label='WhatsApp',
                               widget=forms.TextInput(attrs={'class': CLASSE, 'inputmode': 'tel', 'placeholder': '(21) 98888-7777'}))
    frase = forms.CharField(required=False, max_length=80, label='Sua frase de torcedor',
                            widget=forms.TextInput(attrs={'class': CLASSE, 'placeholder': 'Ex.: Mengão até morrer'}))
    avatar = forms.CharField(label='Avatar', required=False)
    avisos_whatsapp = forms.BooleanField(required=False, label='A staff pode me chamar no WhatsApp')

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_avatar(self):
        codigo = self.cleaned_data.get('avatar') or _avatares.PADRAO
        if codigo not in _avatares.catalogo():
            raise forms.ValidationError('Avatar inválido.')
        if self.usuario is not None and codigo not in _avatares.liberados(self.usuario):
            raise forms.ValidationError('Esse avatar ainda está bloqueado: desbloqueie a conquista correspondente.')
        return codigo

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        existe = User.objects.filter(username__iexact=email).exclude(pk=self.usuario.pk).exists() \
            or User.objects.filter(email__iexact=email).exclude(pk=self.usuario.pk).exists()
        if existe:
            raise forms.ValidationError("Este e-mail já está em uso por outra conta.")
        return email

    def clean_telefone(self):
        try:
            return dados.normalizar_telefone(self.cleaned_data.get('telefone'))
        except ValueError as erro:
            raise forms.ValidationError(str(erro))


class PerguntaSecretaForm(forms.Form):
    pergunta = forms.ChoiceField(choices=PerfilUsuario.PERGUNTAS_SECRETAS, label='Pergunta secreta',
                                 widget=forms.Select(attrs={'class': CLASSE}))
    resposta = forms.CharField(max_length=80, label='Resposta', widget=forms.TextInput(attrs={'class': CLASSE, 'autocomplete': 'off'}))

    def clean_resposta(self):
        resposta = self.cleaned_data['resposta']
        if len(dados._normalizar_resposta(resposta)) < 3:
            raise forms.ValidationError("A resposta precisa ter pelo menos 3 letras ou números.")
        return resposta


class RecuperarSenhaForm(forms.Form):
    email = forms.EmailField(label='E-mail da conta', widget=forms.EmailInput(attrs={'class': CLASSE, 'autocomplete': 'email'}))
    telefone = forms.CharField(required=False, label='WhatsApp cadastrado',
                               widget=forms.TextInput(attrs={'class': CLASSE, 'inputmode': 'tel', 'placeholder': '(21) 98888-7777'}))
    pergunta = forms.ChoiceField(required=False, choices=[('', 'Escolha a pergunta que você cadastrou')] + PerfilUsuario.PERGUNTAS_SECRETAS,
                                 label='Pergunta secreta', widget=forms.Select(attrs={'class': CLASSE}))
    resposta = forms.CharField(required=False, label='Resposta', widget=forms.TextInput(attrs={'class': CLASSE, 'autocomplete': 'off'}))

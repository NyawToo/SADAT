from django import forms
from .models import Usuario
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Nombre de Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese un nombre de usuario único', 'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com', 'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres, incluya números y letras', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña anterior', 'class': 'form-control'})
    )
    tipo = forms.ChoiceField(
        label='Tipo de Usuario',
        choices=Usuario.ROLES,
        widget=forms.Select(attrs={'placeholder': 'Seleccione su tipo de usuario', 'class': 'form-control'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: +57 311 8681638', 'class': 'form-control'})
    )
    direccion = forms.CharField(
        label='Dirección',
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese su dirección completa', 'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2', 'tipo', 'telefono', 'direccion')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = self.cleaned_data['tipo']
        user.telefono = self.cleaned_data['telefono']
        user.direccion = self.cleaned_data['direccion']
        if commit:
            user.save()
        return user
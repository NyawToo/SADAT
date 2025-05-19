from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from empresas.models import MicroempresaIntegral, MicroempresaSatelite

class ClienteRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese un nombre de usuario único', 'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com', 'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres, incluya números y letras', 'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña anterior', 'class': 'form-control'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
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
        fields = ('username', 'email', 'password1', 'password2', 'telefono', 'direccion')
        label= ("Nombre De Usuario", "Correo Electronico", "Contraseña", "Confirmar Contraseña", "Telefono", "Direccion")
    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'cliente'
        user.telefono = self.cleaned_data['telefono']
        user.direccion = self.cleaned_data['direccion']
        if commit:
            user.save()
        return user

class EmpresaIntegralRegistrationForm(UserCreationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese un nombre de usuario único', 'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'placeholder': 'ejemplo@correo.com', 'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres, incluya números y letras', 'class': 'form-control'})
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita la contraseña anterior', 'class': 'form-control'})
    )
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: +57 311 8681638', 'class': 'form-control'})
    )
    direccion = forms.CharField(
        label='Dirección',
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese su dirección completa', 'class': 'form-control', 'rows': 3})
    )
    nombre_empresa = forms.CharField(
        label='Nombre de la empresa',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de su empresa', 'class': 'form-control'})
    )
    descripcion = forms.CharField(
        label='Descripción',
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción de su empresa', 'class': 'form-control', 'rows': 4})
    )
    rut_empresa = forms.CharField(
        label='RUT',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'RUT de la empresa', 'class': 'form-control'})
    )
    imagen = forms.ImageField(
        label='Logo de la empresa',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Sube una imagen para tu empresa'
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2', 'telefono', 'direccion', 
                 'nombre_empresa', 'descripcion', 'rut_empresa', 'imagen')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'integral'
        user.telefono = self.cleaned_data['telefono']
        user.direccion = self.cleaned_data['direccion']
        if commit:
            user.save()
            MicroempresaIntegral.objects.create(
                usuario=user,
                nombre_empresa=self.cleaned_data['nombre_empresa'],
                descripcion=self.cleaned_data['descripcion'],
                imagen=self.cleaned_data['imagen'],
                rut_empresa=self.cleaned_data['rut_empresa']
            )
        return user

class EmpresaSateliteRegistrationForm(UserCreationForm):
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
    telefono = forms.CharField(
        label='Teléfono',
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Ej: +57 311 8681638', 'class': 'form-control'})
    )
    direccion = forms.CharField(
        label='Dirección',
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Ingrese su dirección completa', 'class': 'form-control', 'rows': 3})
    )
    nombre_empresa = forms.CharField(
        label='Nombre de la Empresa',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre de su empresa', 'class': 'form-control'})
    )
    descripcion = forms.CharField(
        label='Descripción',
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción de su empresa', 'class': 'form-control', 'rows': 4})
    )
    rut_empresa = forms.CharField(
        label='RUT de la Empresa',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'RUT de la empresa', 'class': 'form-control'})
    )
    imagen = forms.ImageField(
        label='Logo de la Empresa',
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Sube una imagen para tu empresa'
    )

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2', 'telefono', 'direccion',
                 'nombre_empresa', 'descripcion', 'rut_empresa', 'imagen')
        label= ("Nombre De Usuario", "Correo Electronico", "Contraseña", "Confirmar Contraseña", "Telefono", "Direccion", "Nombre De La Empresa", "Descripcion", "Rut De La Empresa", "Imagen")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo = 'satelite'
        user.telefono = self.cleaned_data['telefono']
        user.direccion = self.cleaned_data['direccion']
        if commit:
            user.save()
            MicroempresaSatelite.objects.create(
                usuario=user,
                nombre_empresa=self.cleaned_data['nombre_empresa'],
                descripcion=self.cleaned_data['descripcion'],
                rut_empresa=self.cleaned_data['rut_empresa'],
                imagen=self.cleaned_data['imagen']
            )
        return user
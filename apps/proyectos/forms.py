from django import forms
from .models import Proyecto
from django.contrib.auth import get_user_model

User = get_user_model()


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombre del proyecto',
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3.5 text-on-surface placeholder:text-slate-400 focus:ring-4 focus:ring-primary/5 transition-all text-sm font-medium',
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Describe el objetivo del proyecto...',
                'rows': 4,
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3.5 text-on-surface placeholder:text-slate-400 focus:ring-4 focus:ring-primary/5 transition-all text-sm resize-none',
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        qs = Proyecto.objects.filter(nombre__iexact=nombre)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe un proyecto con este nombre.')
        return nombre


class AgregarMiembroForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico del usuario',
        widget=forms.EmailInput(attrs={
            'placeholder': 'usuario@ejemplo.com',
            'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3.5 text-on-surface placeholder:text-slate-400 focus:ring-4 focus:ring-primary/5 transition-all text-sm',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('No existe ningún usuario con ese correo electrónico.')
        self.cleaned_data['usuario'] = user
        return email

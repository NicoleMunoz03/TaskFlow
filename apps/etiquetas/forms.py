from django import forms
from .models import Etiqueta


class EtiquetaForm(forms.ModelForm):
    class Meta:
        model = Etiqueta
        fields = ['nombre', 'color']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombre de la etiqueta',
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3 text-on-surface text-sm',
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'w-12 h-10 rounded cursor-pointer border-none',
            }),
        }

from django import forms
from .models import Tarea
from apps.etiquetas.models import Etiqueta
from django.contrib.auth import get_user_model

User = get_user_model()


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['titulo', 'descripcion', 'fecha_limite', 'prioridad', 'columna', 'usuarios', 'etiquetas', 'dependencias']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'placeholder': '¿Qué hay que hacer?',
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3.5 text-on-surface placeholder:text-slate-400 focus:ring-4 focus:ring-primary/5 transition-all text-sm font-medium',
            }),
            'descripcion': forms.Textarea(attrs={
                'placeholder': 'Añade contexto o detalles específicos...',
                'rows': 3,
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3.5 text-on-surface placeholder:text-slate-400 focus:ring-4 focus:ring-primary/5 transition-all text-sm resize-none',
            }),
            'fecha_limite': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3 text-on-surface focus:ring-4 focus:ring-primary/5 transition-all text-sm',
            }),
            'prioridad': forms.Select(attrs={
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3 text-on-surface focus:ring-4 focus:ring-primary/5 transition-all text-sm',
            }),
            'columna': forms.Select(attrs={
                'class': 'w-full bg-surface-container-low border-none rounded-xl px-4 py-3 text-on-surface focus:ring-4 focus:ring-primary/5 transition-all text-sm',
            }),
            'usuarios': forms.CheckboxSelectMultiple(),
            'etiquetas': forms.CheckboxSelectMultiple(),
            'dependencias': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, proyecto=None, tablero=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proyecto_inst = proyecto or (tablero.proyecto if tablero else None)
        self.fields['fecha_limite'].required = True
        self.fields['usuarios'].required = True
        if proyecto:
            self.fields['columna'].queryset = (
                __import__('apps.tableros.models', fromlist=['Columna'])
                .Columna.objects.filter(tablero__proyecto=proyecto)
            )
            # Solo miembros activos en el proyecto para asignar tareas nuevas
            from apps.proyectos.models import UsuarioProyecto
            activos_ids = UsuarioProyecto.objects.filter(
                proyecto=proyecto, activo=True
            ).values_list('usuario_id', flat=True)
            self.fields['usuarios'].queryset = proyecto.miembros.filter(pk__in=activos_ids)
            self.fields['etiquetas'].queryset = Etiqueta.objects.filter(proyecto=proyecto)
            qs_tareas = Tarea.objects.filter(columna__tablero__proyecto=proyecto)
            if self.instance and self.instance.pk:
                qs_tareas = qs_tareas.exclude(pk=self.instance.pk)
            self.fields['dependencias'].queryset = qs_tareas
        elif tablero:
            self.fields['columna'].queryset = tablero.columnas.all()
            qs_tareas = Tarea.objects.filter(columna__tablero=tablero)
            if self.instance and self.instance.pk:
                qs_tareas = qs_tareas.exclude(pk=self.instance.pk)
            self.fields['dependencias'].queryset = qs_tareas

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        proyecto = self.proyecto_inst
        
        if not proyecto:
            return titulo
            
        qs = Tarea.objects.filter(columna__tablero__proyecto=proyecto, titulo__iexact=titulo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise forms.ValidationError('Ya existe una tarea con este título en el proyecto.')
            
        return titulo

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk:
            columna_original = Tarea.objects.get(pk=self.instance.pk).columna
            nueva_columna = cleaned_data.get('columna')
            
            if columna_original.nombre.lower() in ['hecho', 'done', 'completado']:
                if nueva_columna and nueva_columna != columna_original:
                    raise forms.ValidationError('Esta tarea ya está completada y no puede moverse a otra columna.')
        return cleaned_data

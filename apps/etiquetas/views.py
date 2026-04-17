from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Etiqueta
from .forms import EtiquetaForm
from apps.proyectos.models import Proyecto


@login_required
@require_POST
def crear_etiqueta(request, proyecto_pk):
    proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)
    form = EtiquetaForm(request.POST)
    if form.is_valid():
        etiqueta = form.save(commit=False)
        etiqueta.proyecto = proyecto
        if Etiqueta.objects.filter(nombre__iexact=etiqueta.nombre, proyecto=proyecto).exists():
            messages.error(request, 'Ya existe una etiqueta con este nombre en el proyecto.')
        else:
            etiqueta.save()
            messages.success(request, f'Etiqueta "{etiqueta.nombre}" creada.')
    else:
        messages.error(request, 'No se pudo crear la etiqueta.')
    return redirect('proyectos:detalle', pk=proyecto_pk)


@login_required
@require_POST
def eliminar_etiqueta(request, pk):
    etiqueta = get_object_or_404(Etiqueta, pk=pk, proyecto__usuario_proyectos__usuario=request.user, proyecto__usuario_proyectos__activo=True)
    proyecto_pk = etiqueta.proyecto.pk
    
    # Bloquear si la etiqueta tiene tareas asociadas
    if etiqueta.tareas.exists():
        messages.error(request, f'No se puede eliminar la etiqueta "{etiqueta.nombre}" porque está actualmente asignada a una o más tareas.')
        return redirect('proyectos:detalle', pk=proyecto_pk)
        
    nombre = etiqueta.nombre
    etiqueta.delete()
    messages.success(request, f'Etiqueta "{nombre}" eliminada.')
    return redirect('proyectos:detalle', pk=proyecto_pk)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tablero, Columna
from apps.tareas.services import aplicar_filtros
from apps.tareas.forms import TareaForm
from apps.etiquetas.models import Etiqueta


@login_required
def tablero_detail(request, pk):
    tablero = get_object_or_404(
        Tablero,
        pk=pk,
        proyecto__usuario_proyectos__usuario=request.user, proyecto__usuario_proyectos__activo=True,
    )
    proyecto = tablero.proyecto
    columnas = tablero.columnas.prefetch_related(
        'tareas__usuarios',
        'tareas__etiquetas',
    ).all()

    # Filtros
    filtros = {
        'usuario_id': request.GET.get('usuario'),
        'prioridad': request.GET.get('prioridad'),
        'etiqueta_id': request.GET.get('etiqueta'),
        'fecha_limite': request.GET.get('fecha'),
    }

    # Aplicar filtros a las tareas de cada columna
    columnas_data = []
    for columna in columnas:
        tareas_qs = columna.tareas.select_related('columna').prefetch_related('usuarios', 'etiquetas')
        tareas_filtradas = aplicar_filtros(tareas_qs, **{k: v for k, v in filtros.items() if v})
        columnas_data.append({
            'columna': columna,
            'tareas': tareas_filtradas,
        })

    from apps.proyectos.models import UsuarioProyecto
    miembros_activos_ids = UsuarioProyecto.objects.filter(
        proyecto=proyecto, activo=True
    ).values_list('usuario_id', flat=True)
    miembros = proyecto.miembros.filter(pk__in=miembros_activos_ids)
    etiquetas = Etiqueta.objects.filter(proyecto=proyecto)
    form_tarea = TareaForm(proyecto=proyecto)

    return render(request, 'taskflow/tablero/tablero.html', {
        'tablero': tablero,
        'proyecto': proyecto,
        'columnas_data': columnas_data,
        'miembros': miembros,
        'etiquetas': etiquetas,
        'form_tarea': form_tarea,
        'filtros': filtros,
        'prioridades': [('alta', 'Alta'), ('media', 'Media'), ('baja', 'Baja')],
    })


@login_required
def crear_tablero(request, proyecto_pk):
    from apps.proyectos.models import Proyecto
    proyecto = get_object_or_404(Proyecto, pk=proyecto_pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            if Tablero.objects.filter(nombre__iexact=nombre, proyecto=proyecto).exists():
                messages.error(request, 'Ya existe un tablero con ese nombre en este proyecto.')
                return render(request, 'taskflow/tablero/form_tablero.html', {'proyecto': proyecto})
            
            tablero = Tablero.objects.create(nombre=nombre, proyecto=proyecto)
            columnas_default = [('Pendiente', 0), ('En Progreso', 1), ('Hecho', 2)]
            for col_nombre, orden in columnas_default:
                Columna.objects.create(nombre=col_nombre, orden=orden, tablero=tablero)
            messages.success(request, f'Tablero "{nombre}" creado.')
            return redirect('tableros:detalle', pk=tablero.pk)
        else:
            messages.error(request, 'El nombre del tablero es obligatorio.')
    return render(request, 'taskflow/tablero/form_tablero.html', {'proyecto': proyecto})

@login_required
def editar_tablero(request, pk):
    tablero = get_object_or_404(Tablero, pk=pk, proyecto__usuario_proyectos__usuario=request.user, proyecto__usuario_proyectos__activo=True)
    
    # Restricción: solo creador puede modificar o dejamos a cualquier miembro?
    # El usuario general dice "quiero poder editar/eliminar", usualmente lo hace el creador
    if tablero.proyecto.creador != request.user:
        messages.error(request, "Solo el creador del proyecto puede editar tableros.")
        return redirect('proyectos:detalle', pk=tablero.proyecto.pk)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            if Tablero.objects.filter(nombre__iexact=nombre, proyecto=tablero.proyecto).exclude(pk=tablero.pk).exists():
                messages.error(request, 'Ya existe un tablero con ese nombre en este proyecto.')
                return render(request, 'taskflow/tablero/form_tablero.html', {
                    'proyecto': tablero.proyecto,
                    'tablero': tablero
                })
                
            tablero.nombre = nombre
            tablero.save()
            messages.success(request, 'Tablero actualizado.')
            return redirect('proyectos:detalle', pk=tablero.proyecto.pk)
        else:
            messages.error(request, 'El nombre del tablero es obligatorio.')
            
    return render(request, 'taskflow/tablero/form_tablero.html', {
        'proyecto': tablero.proyecto,
        'tablero': tablero
    })


@login_required
def eliminar_tablero(request, pk):
    tablero = get_object_or_404(Tablero, pk=pk, proyecto__usuario_proyectos__usuario=request.user, proyecto__usuario_proyectos__activo=True)
    proyecto_pk = tablero.proyecto.pk
    
    if tablero.proyecto.creador != request.user:
        messages.error(request, "Solo el creador del proyecto puede eliminar tableros.")
        return redirect('proyectos:detalle', pk=proyecto_pk)

    if request.method == 'POST':
        nombre = tablero.nombre
        tablero.delete()
        messages.success(request, f'Tablero "{nombre}" eliminado correctamente.')

    return redirect('proyectos:detalle', pk=proyecto_pk)


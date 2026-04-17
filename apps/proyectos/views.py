from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Proyecto, UsuarioProyecto
from .forms import ProyectoForm, AgregarMiembroForm
from apps.tareas.models import Tarea


@login_required
def lista_proyectos(request):
    proyectos = Proyecto.objects.filter(
        usuario_proyectos__usuario=request.user, 
        usuario_proyectos__activo=True
    ).prefetch_related('miembros').distinct()
    return render(request, 'taskflow/proyecto/proyectos.html', {
        'proyectos': proyectos,
    })


@login_required
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            # Agregar al creador como miembro
            UsuarioProyecto.objects.create(usuario=request.user, proyecto=proyecto)
            messages.success(request, f'Proyecto "{proyecto.nombre}" creado exitosamente.')
            return redirect('proyectos:detalle', pk=proyecto.pk)
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ProyectoForm()
    return render(request, 'taskflow/proyecto/form.html', {
        'form': form,
        'titulo': 'Nuevo Proyecto',
        'accion': 'Crear Proyecto',
    })


@login_required
def detalle_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)
    tableros = proyecto.tableros.prefetch_related('columnas').all()
    tareas_recientes = Tarea.objects.filter(
        columna__tablero__proyecto=proyecto
    ).select_related('columna', 'columna__tablero').prefetch_related('usuarios').order_by('-fecha_creacion')[:5]
    agregar_form = AgregarMiembroForm()

    # Columnas que se consideran "activas" (bloquean inhabilitación)
    COLUMNAS_ACTIVAS = ['pendiente', 'en progreso']

    # Iterar sobre TODOS los UsuarioProyecto (activos e inactivos)
    miembros_info = []
    for up in UsuarioProyecto.objects.filter(proyecto=proyecto).select_related('usuario'):
        miembro = up.usuario
        tareas_bloqueantes = Tarea.objects.filter(
            columna__tablero__proyecto=proyecto,
            usuarios=miembro,
            columna__nombre__iregex=r'^(pendiente|en progreso)$',
        ).count()
        puede_inhabilitar = (
            request.user == proyecto.creador
            and miembro != proyecto.creador
            and up.activo
            and tareas_bloqueantes == 0
        )
        miembros_info.append({
            'usuario': miembro,
            'activo': up.activo,
            'tareas_bloqueantes': tareas_bloqueantes,
            'puede_inhabilitar': puede_inhabilitar,
            'es_creador': miembro == proyecto.creador,
        })

    activos_count = sum(1 for m in miembros_info if m['activo'])

    return render(request, 'taskflow/proyecto/detalle_proy.html', {
        'proyecto': proyecto,
        'tableros': tableros,
        'tareas_recientes': tareas_recientes,
        'agregar_form': agregar_form,
        'miembros_info': miembros_info,
        'activos_count': activos_count,
        'es_creador': request.user == proyecto.creador,
    })


@login_required
def editar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)
    # Solo el creador puede editar
    if proyecto.creador and proyecto.creador != request.user:
        messages.error(request, 'Solo el creador del proyecto puede editarlo.')
        return redirect('proyectos:detalle', pk=proyecto.pk)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, instance=proyecto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyecto actualizado correctamente.')
            return redirect('proyectos:detalle', pk=proyecto.pk)
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ProyectoForm(instance=proyecto)
    return render(request, 'taskflow/proyecto/form.html', {
        'form': form,
        'proyecto': proyecto,
        'titulo': f'Editar: {proyecto.nombre}',
        'accion': 'Guardar Cambios',
    })


@login_required
def eliminar_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)
    # Solo el creador puede eliminar
    if proyecto.creador and proyecto.creador != request.user:
        messages.error(request, 'Solo el creador del proyecto puede eliminarlo.')
        return redirect('proyectos:detalle', pk=proyecto.pk)
    if request.method == 'POST':
        nombre = proyecto.nombre
        proyecto.delete()
        messages.success(request, f'Proyecto "{nombre}" eliminado.')
        return redirect('proyectos:lista')
    return redirect('proyectos:detalle', pk=proyecto.pk)


@login_required
def agregar_miembro(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)
    
    if proyecto.creador != request.user:
        messages.error(request, 'Solo el creador del proyecto puede agregar miembros.')
        return redirect('proyectos:detalle', pk=proyecto.pk)

    if request.method == 'POST':
        form = AgregarMiembroForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            if UsuarioProyecto.objects.filter(usuario=usuario, proyecto=proyecto).exists():
                messages.warning(request, 'Este usuario ya es miembro del proyecto.')
            else:
                UsuarioProyecto.objects.create(usuario=usuario, proyecto=proyecto)
                
                # Enviar correo de notificación (Asíncrono para evitar bloqueos)
                from apps.notificaciones.services import enviar_correo_asincrono
                subject = f'[TaskFlow] Te han añadido al proyecto: {proyecto.nombre}'
                body = (
                    f'Hola {usuario.get_short_name()},\n\n'
                    f'El creador del proyecto "{proyecto.nombre}" te ha añadido como miembro del equipo.\n'
                    f'¡Ya puedes acceder a los tableros y tareas!\n\n'
                    f'— TaskFlow Pro'
                )
                enviar_correo_asincrono(subject, body, [usuario.email])
                
                messages.success(request, f'{usuario.nombre} fue agregado al proyecto.')
        else:
            messages.error(request, 'No se pudo agregar el usuario.')
    return redirect('proyectos:detalle', pk=proyecto.pk)


@login_required
def inhabilitar_miembro(request, pk, usuario_pk):
    """Inhabilita (soft-disable) a un miembro del proyecto.

    Reglas:
    - Solo el creador del proyecto puede inhabilitar miembros.
    - No se puede inhabilitar al propio creador.
    - Si el miembro tiene tareas en columnas 'Pendiente' o 'En Progreso', se bloquea.
    - El registro UsuarioProyecto NO se elimina para preservar el historial de tareas.
    """
    proyecto = get_object_or_404(Proyecto, pk=pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)

    if proyecto.creador != request.user:
        messages.error(request, 'Solo el creador del proyecto puede inhabilitar miembros.')
        return redirect('proyectos:detalle', pk=proyecto.pk)

    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    miembro = get_object_or_404(Usuario, pk=usuario_pk)

    if miembro == proyecto.creador:
        messages.error(request, 'No puedes inhabilitar al creador del proyecto.')
        return redirect('proyectos:detalle', pk=proyecto.pk)

    up = get_object_or_404(UsuarioProyecto, usuario=miembro, proyecto=proyecto)

    if not up.activo:
        messages.warning(request, f'{miembro.nombre} ya está inactivo en este proyecto.')
        return redirect('proyectos:detalle', pk=proyecto.pk)

    # Bloquear si tiene tareas en Pendiente o En Progreso
    tareas_bloqueantes = Tarea.objects.filter(
        columna__tablero__proyecto=proyecto,
        usuarios=miembro,
        columna__nombre__iregex=r'^(pendiente|en progreso)$',
    ).count()

    if tareas_bloqueantes > 0:
        messages.error(
            request,
            f'No se puede inhabilitar a {miembro.nombre}: tiene {tareas_bloqueantes} '
            f'tarea(s) en Pendiente o En Progreso. Reasígnalas primero.'
        )
        return redirect('proyectos:detalle', pk=proyecto.pk)

    if request.method == 'POST':
        up.activo = False
        up.save()
        messages.success(request, f'{miembro.nombre} fue inhabilitado del proyecto. Su historial de tareas se conserva.')

    return redirect('proyectos:detalle', pk=proyecto.pk)

@login_required
def habilitar_miembro(request, pk, usuario_pk):
    """Habilita a un miembro previamente inhabilitado en el proyecto.

    Reglas:
    - Solo el creador del proyecto puede habilitar miembros.
    """
    proyecto = get_object_or_404(Proyecto, pk=pk, usuario_proyectos__usuario=request.user, usuario_proyectos__activo=True)

    if proyecto.creador != request.user:
        messages.error(request, 'Solo el creador del proyecto puede habilitar miembros.')
        return redirect('proyectos:detalle', pk=proyecto.pk)

    from django.contrib.auth import get_user_model
    Usuario = get_user_model()
    miembro = get_object_or_404(Usuario, pk=usuario_pk)

    up = get_object_or_404(UsuarioProyecto, usuario=miembro, proyecto=proyecto)

    if up.activo:
        messages.warning(request, f'{miembro.nombre} ya está activo en este proyecto.')
        return redirect('proyectos:detalle', pk=proyecto.pk)

    if request.method == 'POST':
        up.activo = True
        up.save()
        messages.success(request, f'{miembro.nombre} fue habilitado de nuevo en el proyecto.')

    return redirect('proyectos:detalle', pk=proyecto.pk)

from django.conf import settings
from django.db import models


class Proyecto(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    creador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='proyectos_creados',
        verbose_name='Creador',
    )
    miembros = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UsuarioProyecto',
        related_name='proyectos',
        verbose_name='Miembros',
    )

    class Meta:
        verbose_name = 'proyecto'
        verbose_name_plural = 'proyectos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    def get_total_tareas(self):
        from apps.tareas.models import Tarea
        return Tarea.objects.filter(columna__tablero__proyecto=self).count()

    def get_tareas_completadas(self):
        from apps.tareas.models import Tarea
        return Tarea.objects.filter(columna__tablero__proyecto=self, columna__nombre='Hecho').count()

    def get_progreso(self):
        total = self.get_total_tareas()
        if total == 0:
            return 0
        return round((self.get_tareas_completadas() / total) * 100)


class UsuarioProyecto(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usuario_proyectos',
    )
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='usuario_proyectos',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo en el proyecto',
        help_text='Deshabilita al miembro sin borrar su historial de tareas.',
    )

    class Meta:
        verbose_name = 'miembro del proyecto'
        verbose_name_plural = 'miembros del proyecto'
        unique_together = ('usuario', 'proyecto')

    def __str__(self):
        estado = 'activo' if self.activo else 'inactivo'
        return f'{self.usuario} en {self.proyecto} ({estado})'

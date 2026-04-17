from django.conf import settings
from django.db import models


class Tarea(models.Model):
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    titulo = models.CharField(max_length=300, verbose_name='Título')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    fecha_limite = models.DateField(null=True, blank=True, verbose_name='Fecha límite')
    prioridad = models.CharField(
        max_length=5,
        choices=PRIORIDAD_CHOICES,
        default='media',
        verbose_name='Prioridad',
    )
    columna = models.ForeignKey(
        'tableros.Columna',
        on_delete=models.CASCADE,
        related_name='tareas',
        verbose_name='Columna',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='TareaUsuario',
        related_name='tareas',
        blank=True,
        verbose_name='Usuarios asignados',
    )
    etiquetas = models.ManyToManyField(
        'etiquetas.Etiqueta',
        through='TareaEtiqueta',
        related_name='tareas',
        blank=True,
        verbose_name='Etiquetas',
    )
    dependencias = models.ManyToManyField(
        'self',
        through='TareaDependencia',
        symmetrical=False,
        related_name='es_dependencia_de',
        blank=True,
        verbose_name='Dependencias',
    )


    class Meta:
        verbose_name = 'tarea'
        verbose_name_plural = 'tareas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo

    def get_prioridad_color(self):
        colores = {
            'alta': 'error-container',
            'media': 'secondary-container',
            'baja': 'tertiary-container',
        }
        return colores.get(self.prioridad, 'secondary-container')

    def get_prioridad_text_color(self):
        colores = {
            'alta': 'on-error-container',
            'media': 'on-secondary-container',
            'baja': 'on-tertiary-container',
        }
        return colores.get(self.prioridad, 'on-secondary-container')

    def es_vencida(self):
        from django.utils import timezone
        if self.fecha_limite:
            return self.fecha_limite < timezone.now().date()
        return False

    @property
    def esta_bloqueada(self):
        for dep in self.dependencias.all():
            if dep.columna.nombre.lower() not in ['hecho', 'done', 'completado']:
                return True
        return False



class TareaUsuario(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='tarea_usuarios')
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usuario_tareas',
    )

    class Meta:
        verbose_name = 'asignación de tarea'
        verbose_name_plural = 'asignaciones de tarea'
        unique_together = ('tarea', 'usuario')

    def __str__(self):
        return f'{self.usuario} → {self.tarea}'


class TareaEtiqueta(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    etiqueta = models.ForeignKey('etiquetas.Etiqueta', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tarea', 'etiqueta')


class TareaDependencia(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='dependencias_configuradas')
    depende_de = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='bloquea_a_tareas')

    class Meta:
        verbose_name = 'dependencia de tarea'
        verbose_name_plural = 'dependencias de tareas'
        unique_together = ('tarea', 'depende_de')

    def __str__(self):
        return f'{self.tarea} depende de {self.depende_de}'

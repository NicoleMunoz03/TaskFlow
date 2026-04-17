from django.db import models


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, verbose_name='Nombre')
    color = models.CharField(max_length=7, default='#0053dc', verbose_name='Color (hex)')
    proyecto = models.ForeignKey(
        'proyectos.Proyecto',
        on_delete=models.CASCADE,
        related_name='etiquetas',
        verbose_name='Proyecto',
    )

    class Meta:
        verbose_name = 'etiqueta'
        verbose_name_plural = 'etiquetas'
        ordering = ['nombre']
        unique_together = ('nombre', 'proyecto')

    def __str__(self):
        return f'{self.nombre} ({self.proyecto.nombre})'

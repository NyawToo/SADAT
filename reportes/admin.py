from django.contrib import admin
from .models import Queja

@admin.register(Queja)
class QuejaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'estado', 'fecha_creacion', 'fecha_resolucion')
    list_filter = ('estado', 'tipo', 'fecha_creacion')
    search_fields = ('usuario__username', 'descripcion')
    date_hierarchy = 'fecha_creacion'
    
    readonly_fields = ('fecha_creacion', 'fecha_resolucion')
    
    fieldsets = (
        ('Información de la Queja', {
            'fields': ('usuario', 'tipo', 'descripcion', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_resolucion')
        })
    )

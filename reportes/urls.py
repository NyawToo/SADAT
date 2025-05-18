from django.urls import path
from . import views, views_reportes

urlpatterns = [
    # Rutas existentes
    path('global/', views.reporte_global, name='reporte_global'),
    path('ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('quejas/', views.quejas, name='quejas'),
    
    # Nuevas rutas para reportes personalizados
    path('cliente/', views_reportes.reporte_cliente, name='reporte_cliente'),
    path('empresa/<int:empresa_id>/', views_reportes.reporte_empresa, name='reporte_empresa'),
    path('admin/panel/', views_reportes.panel_admin_reportes, name='panel_admin_reportes'),
    
    # Rutas para exportación
    path('exportar/cliente/<str:formato>/', views_reportes.exportar_reporte, 
         {'tipo_reporte': 'cliente'}, name='exportar_reporte_cliente'),
    path('exportar/empresa/<int:empresa_id>/<str:formato>/', views_reportes.exportar_reporte,
         {'tipo_reporte': 'empresa'}, name='exportar_reporte_empresa'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.log_notificaciones, name='log_notificaciones'),
    path('reintentar/<int:notificacion_id>/', views.reintentar_envio, name='reintentar_envio'),
    path('limpiar/', views.limpiar_registros, name='limpiar_registros'),
]
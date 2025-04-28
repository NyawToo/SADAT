from django.urls import path
from . import views

urlpatterns = [
    path('global/', views.reporte_global, name='reporte_global'),
    path('ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('quejas/', views.quejas, name='quejas'),
]
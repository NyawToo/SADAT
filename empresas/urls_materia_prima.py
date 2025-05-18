from django.urls import path
from . import views_materia_prima

urlpatterns = [
    path('materia-prima/dashboard/', views_materia_prima.dashboard_materia_prima, name='dashboard_materia_prima'),
    path('materia-prima/categorias/', views_materia_prima.gestionar_categorias_materia_prima, name='gestionar_categorias_materia_prima'),
    path('materia-prima/categorias/eliminar/<int:categoria_id>/', views_materia_prima.eliminar_categoria_materia_prima, name='eliminar_categoria_materia_prima'),
    path('materia-prima/inventario/', views_materia_prima.gestionar_materia_prima, name='gestionar_materia_prima'),
    path('materia-prima/inventario/eliminar/<int:materia_prima_id>/', views_materia_prima.eliminar_materia_prima, name='eliminar_materia_prima'),
    path('materia-prima/movimientos/', views_materia_prima.movimientos_materia_prima, name='movimientos_materia_prima'),
]
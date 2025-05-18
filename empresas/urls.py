from django.urls import path, include
from . import views, views_producto

urlpatterns = [
    path('servicios/agregar/', views.agregar_servicios, name='agregar_servicios'),
    path('productos/crear/', views_producto.crear_producto, name='crear_producto'),
    path('productos/<int:producto_id>/editar/', views_producto.editar_producto, name='editar_producto'),
    path('productos/<int:producto_id>/eliminar/', views_producto.eliminar_producto, name='eliminar_producto'),
    path('catalogo-integrales/', views.catalogo_integrales, name='catalogo_integrales'),
    path('catalogo-satelites/', views.catalogo_satelites, name='catalogo_satelites'),
    path('catalogo/', views.catalogo_empresas, name='catalogo_empresas'),
    path('detalle-integral/<int:pk>/', views.detalle_empresa_integral, name='detalle_empresa_integral'),
    path('detalle-satelite/<int:pk>/', views.detalle_empresa_satelite, name='detalle_empresa_satelite'),
    path('materia-prima/', views.gestionar_materia_prima, name='gestionar_materia_prima'),
    path('productos/', views.gestionar_productos, name='gestionar_productos'),
    path('producto/<int:producto_id>/agregar-comentario/', views_producto.agregar_comentario, name='agregar_comentario'),
    path('producto/<int:producto_id>/calificar/', views_producto.calificar_producto, name='calificar_producto'),
    path('dar-like/<int:comentario_id>/', views_producto.dar_like, name='dar_like'),
    path('dar-dislike/<int:comentario_id>/', views_producto.dar_dislike, name='dar_dislike'),
    # URLs de materia prima
    path('', include('empresas.urls_materia_prima')),
]
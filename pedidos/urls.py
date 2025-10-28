from django.urls import path
from . import views, views_pedidos_empresa, views_producto, views_confeccion, views_gestion

urlpatterns = [
    # Rutas para gestión de solicitudes de confección (universales para integral y satélite)
    path('confeccion/gestionar/', views_gestion.gestionar_solicitudes_confeccion_universal, name='gestionar_solicitudes_confeccion'),
    path('confeccion/actualizar-estado/<int:solicitud_id>/', views_confeccion.actualizar_estado_solicitud_universal, name='actualizar_estado_solicitud'),
    path('confeccion/cotizar/<int:solicitud_id>/', views_confeccion.cotizar_solicitud_universal, name='cotizar_solicitud'),
    path('solicitudes/cotizar/<int:solicitud_id>/', views_confeccion.cotizar_solicitud_universal, name='cotizar_solicitud_alt'),
    path('confeccion/responder-cotizacion/<int:solicitud_id>/', views.responder_cotizacion_confeccion, name='responder_cotizacion_confeccion'),
    path('responder-cotizacion/<int:pedido_id>/', views.responder_cotizacion_personalizada, name='responder_cotizacion_personalizada'),
    path('empresa/pedidos/', views_pedidos_empresa.lista_pedidos_empresa, name='lista_pedidos_empresa'),
    path('lista/', views.lista_pedidos, name='lista_pedidos'),
    path('empresa/pedidos/<int:pedido_id>/actualizar/', views_pedidos_empresa.actualizar_estado_pedido, name='actualizar_estado_pedido'),
    path('solicitar-confeccion/', views.solicitar_confeccion, name='solicitar_confeccion'),
    path('solicitar-confeccion/<int:servicio_id>/', views.solicitar_confeccion, name='solicitar_confeccion_servicio'),
    path('solicitar-pedido-personalizado/<int:empresa_id>/', views.solicitar_pedido_personalizado, name='solicitar_pedido_personalizado'),
    path('categorias/', views.categorias, name='categorias'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('carrito/', views.carrito, name='ver_carrito'),
    path('gestionar-pedidos/', views.gestionar_pedidos, name='gestionar_pedidos'),
    path('gestionar-pedidos-personalizados/', views.gestionar_pedidos_personalizados, name='gestionar_pedidos_personalizados'),
    path('actualizar-pedido-personalizado/<int:pedido_id>/', views.actualizar_pedido_personalizado, name='actualizar_pedido_personalizado'),
    path('gestionar-solicitudes-confeccion/', views.gestionar_solicitudes_confeccion, name='gestionar_solicitudes_confeccion'),
    path('lista-productos/', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('pedido/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'), # URL para ver detalle de un pedido
    path('agregar-al-carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar-del-carrito/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('editar-categoria/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('eliminar-categoria/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),
]
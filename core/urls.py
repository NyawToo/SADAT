from django.urls import path
from . import views

urlpatterns = [
    path('configuracion-sistema/', views.configuracion_sistema, name='configuracion_sistema'),
    path('crear-superadmin/', views.crear_superadmin, name='crear_superadmin'),
    path('gestionar-usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('', views.inicio, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/cliente/', views.registro_cliente, name='registro_cliente'),
    path('registro/integral/', views.registro_integral, name='registro_integral'),
    path('registro/satelite/', views.registro_satelite, name='registro_satelite'),
    path('perfil/', views.perfil, name='perfil'),
    path('editar-usuario/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    # La vista responder_cotizacion_personalizada se ha movido a pedidos.urls
    # Las vistas de pago se han movido al módulo de pagos
]
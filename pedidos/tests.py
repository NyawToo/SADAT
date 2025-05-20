from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import SolicitudConfeccion, Pedido, DetallePedido, Carrito, ItemCarrito
from empresas.models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado
from core.models import Usuario
from decimal import Decimal
import json

class SolicitudesConfeccionTests(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='test_user',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            tipo='cliente'
        )
        
        # Crear usuario empresa
        self.empresa_user = get_user_model().objects.create_user(
            username='empresa_test',
            email='empresa@test.com',
            password='empresapass123',
            first_name='Empresa',
            last_name='Test',
            tipo='integral',
            is_staff=True
        )
        
        # Crear empresa de prueba
        self.empresa = MicroempresaIntegral.objects.create(
            usuario=self.empresa_user,
            nombre_empresa='Empresa Test',
            rut_empresa='123456789',
            descripcion='Empresa de prueba'
        )

        # Crear usuario empresa satélite
        self.empresa_satelite_user = get_user_model().objects.create_user(
            username='empresa_satelite_test',
            email='satelite@test.com',
            password='satelitepass123',
            first_name='Empresa',
            last_name='Satélite',
            tipo='satelite',
            is_staff=True
        )
        
        # Crear empresa satélite
        self.empresa_satelite = MicroempresaSatelite.objects.create(
            usuario=self.empresa_satelite_user,
            nombre_empresa='Empresa Satélite Test',
            rut_empresa='987654321',
            descripcion='Empresa satélite de prueba'
        )
        
        # Crear solicitud de prueba
        self.solicitud = SolicitudConfeccion.objects.create(
            cliente=self.user,
            empresa_integral=self.empresa,
            empresa_satelite=self.empresa_satelite,
            descripcion='Solicitud de prueba',
            cantidad_prendas=10,
            estado='pendiente',
            fecha_entrega_requerida='2024-12-31'
        )

    def test_crear_solicitud_confeccion(self):
        """Prueba la creación de una solicitud de confección"""
        self.client.login(email='test@test.com', password='testpass123')
        data = {
            'empresa_integral': self.empresa.id,
            'empresa_satelite': self.empresa_satelite.id,
            'descripcion': 'Nueva solicitud de prueba',
            'cantidad_prendas': 5,
            'fecha_entrega_requerida': '2024-12-31'
        }
        response = self.client.post(reverse('crear_solicitud_confeccion'), data)
        self.assertEqual(response.status_code, 302)  # Redirección después de crear
        self.assertTrue(SolicitudConfeccion.objects.filter(descripcion='Nueva solicitud de prueba').exists())

    def test_cotizar_solicitud(self):
        """Prueba el proceso de cotización de una solicitud"""
        self.client.login(email='test@test.com', password='testpass123')
        data = {
            'precio_por_prenda': '25000',
            'tiempo_estimado': '5',
            'comentarios': 'Cotización de prueba'
        }
        response = self.client.post(
            reverse('cotizar_solicitud', kwargs={'solicitud_id': self.solicitud.id}),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.precio_por_prenda, Decimal('25000'))

class CarritoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='testpass123',
            first_name='Cliente',
            last_name='Test',
            tipo='cliente'
        )
        
        # Crear usuario empresa
        self.empresa_user = get_user_model().objects.create_user(
            username='empresa_test',
            email='empresa@test.com',
            password='empresapass123',
            first_name='Empresa',
            last_name='Test',
            tipo='integral',
            is_staff=True
        )
        
        # Crear empresa de prueba
        self.empresa = MicroempresaIntegral.objects.create(
            usuario=self.empresa_user,
            nombre_empresa='Empresa Test',
            rut_empresa='123456789',
            descripcion='Empresa de prueba'
        )
        
        self.producto = ProductoTerminado.objects.create(
            empresa=self.empresa,
            nombre='Producto Test',
            descripcion='Producto de prueba',
            precio=Decimal('50000'),
            stock=100
        )

    def test_agregar_al_carrito(self):
        """Prueba agregar un producto al carrito"""
        self.client.login(email='cliente@test.com', password='testpass123')
        data = {
            'producto_id': self.producto.id,
            'cantidad': 2
        }
        response = self.client.post(reverse('agregar_al_carrito'), data)
        self.assertEqual(response.status_code, 302)
        carrito = Carrito.objects.get(usuario=self.user)
        self.assertEqual(carrito.items.count(), 1)
        self.assertEqual(carrito.items.first().cantidad, 2)

    def test_actualizar_carrito(self):
        """Prueba actualizar la cantidad de un producto en el carrito"""
        self.client.login(email='cliente@test.com', password='testpass123')
        carrito = Carrito.objects.create(usuario=self.user)
        item = ItemCarrito.objects.create(
            carrito=carrito,
            producto=self.producto,
            cantidad=1
        )
        
        data = {
            'item_id': item.id,
            'cantidad': 3
        }
        response = self.client.post(reverse('actualizar_carrito'), data)
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 3)

class PedidoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='testpass123',
            first_name='Cliente',
            last_name='Test',
            tipo='cliente'
        )
        
        # Crear usuario empresa
        self.empresa_user = get_user_model().objects.create_user(
            username='empresa_test',
            email='empresa@test.com',
            password='empresapass123',
            first_name='Empresa',
            last_name='Test',
            tipo='integral',
            is_staff=True
        )
        
        # Crear empresa de prueba
        self.empresa = MicroempresaIntegral.objects.create(
            usuario=self.empresa_user,
            nombre_empresa='Empresa Test',
            rut_empresa='123456789',
            descripcion='Empresa de prueba'
        )
        
        self.producto = ProductoTerminado.objects.create(
            empresa=self.empresa,
            nombre='Producto Test',
            descripcion='Producto de prueba',
            precio=Decimal('50000'),
            stock=100
        )

    def test_crear_pedido(self):
        """Prueba la creación de un pedido desde el carrito"""
        self.client.login(email='cliente@test.com', password='testpass123')
        carrito = Carrito.objects.create(usuario=self.user)
        ItemCarrito.objects.create(
            carrito=carrito,
            producto=self.producto,
            cantidad=2
        )
        
        response = self.client.post(reverse('crear_pedido'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Pedido.objects.filter(cliente=self.user).exists())
        pedido = Pedido.objects.get(cliente=self.user)
        self.assertEqual(pedido.detalles.count(), 1)
        self.assertEqual(pedido.detalles.first().cantidad, 2)

    def test_cancelar_pedido(self):
        """Prueba la cancelación de un pedido"""
        self.client.login(email='cliente@test.com', password='testpass123')
        pedido = Pedido.objects.create(
            cliente=self.user,
            estado='PENDIENTE',
            total=Decimal('100000')
        )
        DetallePedido.objects.create(
            pedido=pedido,
            producto=self.producto,
            cantidad=2,
            precio_unitario=Decimal('50000')
        )
        
        response = self.client.post(reverse('cancelar_pedido', kwargs={'pedido_id': pedido.id}))
        self.assertEqual(response.status_code, 302)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'CANCELADO')

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Transaccion
from pedidos.models import Pedido
from empresas.models import MicroempresaIntegral, ProductoTerminado
from decimal import Decimal
import json

class TransaccionTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear usuario cliente
        self.user = get_user_model().objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='clientepass123',
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
        
        # Crear empresa
        self.empresa = MicroempresaIntegral.objects.create(
            usuario=self.empresa_user,
            nombre_empresa='Empresa Test',
            rut_empresa='123456789',
            descripcion='Empresa de prueba'
        )
        
        # Crear producto
        self.producto = ProductoTerminado.objects.create(
            empresa=self.empresa,
            nombre='Producto Test',
            descripcion='Producto de prueba',
            precio=Decimal('50000'),
            stock=100
        )
        
        # Crear pedido
        self.pedido = Pedido.objects.create(
            cliente=self.user,
            estado='PENDIENTE',
            total=Decimal('100000')
        )

    def test_crear_transaccion(self):
        """Prueba la creación de una nueva transacción"""
        self.client.login(email='cliente@test.com', password='clientepass123')
        data = {
            'pedido': self.pedido.id,
            'monto': '100000',
            'metodo_pago': 'TARJETA'
        }
        response = self.client.post(reverse('crear_transaccion'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Transaccion.objects.filter(pedido=self.pedido).exists())

    def test_procesar_pago(self):
        """Prueba el procesamiento de un pago"""
        self.client.login(email='cliente@test.com', password='clientepass123')
        transaccion = Transaccion.objects.create(
            pedido=self.pedido,
            monto=Decimal('100000'),
            metodo_pago='TARJETA',
            estado='PENDIENTE'
        )
        
        data = {
            'token': 'tok_visa',  # Token de prueba de Stripe
            'transaccion_id': transaccion.id
        }
        response = self.client.post(
            reverse('procesar_pago', kwargs={'transaccion_id': transaccion.id}),
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'COMPLETADA')

    def test_cancelar_transaccion(self):
        """Prueba la cancelación de una transacción"""
        self.client.login(email='cliente@test.com', password='clientepass123')
        transaccion = Transaccion.objects.create(
            pedido=self.pedido,
            monto=Decimal('100000'),
            metodo_pago='TARJETA',
            estado='PENDIENTE'
        )
        
        response = self.client.post(reverse('cancelar_transaccion', kwargs={'transaccion_id': transaccion.id}))
        self.assertEqual(response.status_code, 302)
        transaccion.refresh_from_db()
        self.assertEqual(transaccion.estado, 'CANCELADA')

    def test_historial_transacciones(self):
        """Prueba la visualización del historial de transacciones"""
        self.client.login(email='cliente@test.com', password='clientepass123')
        # Crear algunas transacciones de prueba
        Transaccion.objects.create(
            pedido=self.pedido,
            monto=Decimal('100000'),
            metodo_pago='TARJETA',
            estado='COMPLETADA'
        )
        Transaccion.objects.create(
            pedido=self.pedido,
            monto=Decimal('50000'),
            metodo_pago='TRANSFERENCIA',
            estado='PENDIENTE'
        )
        
        response = self.client.get(reverse('historial_transacciones'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['transacciones']), 2)

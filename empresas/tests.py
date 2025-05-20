from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import MicroempresaIntegral, MicroempresaSatelite, ProductoTerminado, Maquina, Servicio
from .models_materia_prima import MateriaPrima
from decimal import Decimal

class EmpresaIntegralTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear usuario administrador
        self.admin = get_user_model().objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='Test',
            tipo='superusuario',
            is_staff=True,
            is_superuser=True
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
            nombre_empresa='Empresa Integral Test',
            rut_empresa='123456789',
            descripcion='Empresa integral de prueba'
        )

    def test_registrar_empresa_integral(self):
        """Prueba el registro de una nueva empresa integral"""
        self.client.login(email='admin@test.com', password='adminpass123')
        data = {
            'nombre_empresa': 'Nueva Empresa Integral',
            'rut_empresa': '987654321',
            'descripcion': 'Nueva empresa integral de prueba'
        }
        response = self.client.post(reverse('registrar_empresa_integral'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MicroempresaIntegral.objects.filter(nit='987654321').exists())

    def test_actualizar_empresa_integral(self):
        """Prueba la actualización de datos de una empresa integral"""
        self.client.login(email='admin@test.com', password='adminpass123')
        data = {
            'nombre_empresa': 'Empresa Actualizada',
            'descripcion': 'Descripción actualizada'
        }
        response = self.client.post(
            reverse('actualizar_empresa_integral', kwargs={'empresa_id': self.empresa.id}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.nombre, 'Empresa Actualizada')

class EmpresaSateliteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = get_user_model().objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='adminpass123',
            first_name='Admin',
            last_name='Test',
            tipo='superusuario',
            is_staff=True,
            is_superuser=True
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
        
        # Crear empresa satélite de prueba
        self.empresa = MicroempresaSatelite.objects.create(
            usuario=self.empresa_satelite_user,
            nombre_empresa='Empresa Satélite Test',
            rut_empresa='123456789',
            descripcion='Empresa satélite de prueba'
        )

    def test_registrar_empresa_satelite(self):
        """Prueba el registro de una nueva empresa satélite"""
        self.client.login(email='admin@test.com', password='adminpass123')
        data = {
            'nombre_empresa': 'Nueva Empresa Satélite',
            'rut_empresa': '987654321',
            'descripcion': 'Nueva empresa satélite de prueba'
        }
        response = self.client.post(reverse('registrar_empresa_satelite'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MicroempresaSatelite.objects.filter(nit='987654321').exists())

class ProductoTests(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_crear_producto(self):
        """Prueba la creación de un nuevo producto"""
        data = {
            'nombre': 'Nuevo Producto',
            'descripcion': 'Descripción del nuevo producto',
            'precio': '75000',
            'stock': '50'
        }
        response = self.client.post(
            reverse('crear_producto', kwargs={'empresa_id': self.empresa.id}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProductoTerminado.objects.filter(nombre='Nuevo Producto').exists())

    def test_actualizar_producto(self):
        """Prueba la actualización de un producto existente"""
        data = {
            'nombre': 'Producto Actualizado',
            'descripcion': 'Descripción actualizada',
            'precio': '60000',
            'stock': '75'
        }
        response = self.client.post(
            reverse('actualizar_producto', kwargs={'producto_id': self.producto.id}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Producto Actualizado')
        self.assertEqual(self.producto.precio, Decimal('60000'))

class MateriaPrimaTests(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_registrar_materia_prima(self):
        """Prueba el registro de materia prima"""
        data = {
            'nombre': 'Tela Algodón',
            'descripcion': 'Tela de algodón 100%',
            'cantidad': '100',
            'unidad_medida': 'METROS'
        }
        response = self.client.post(
            reverse('registrar_materia_prima', kwargs={'empresa_id': self.empresa.id}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MateriaPrima.objects.filter(nombre='Tela Algodón').exists())

class MaquinariaTests(TestCase):
    def setUp(self):
        self.client = Client()
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

    def test_registrar_maquina(self):
        """Prueba el registro de maquinaria"""
        data = {
            'nombre': 'Máquina de Coser Industrial',
            'descripcion': 'Máquina de coser de alta velocidad',
            'cantidad': '2',
            'estado': 'ACTIVO'
        }
        response = self.client.post(
            reverse('registrar_maquina', kwargs={'empresa_id': self.empresa.id}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Maquina.objects.filter(nombre='Máquina de Coser Industrial').exists())

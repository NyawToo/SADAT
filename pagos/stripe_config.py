import os
import stripe
from django.conf import settings
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar Stripe con las claves de API
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Configurar el dominio para las redirecciones
DOMAIN = os.environ.get('DOMAIN', 'https://sadat-ezff.onrender.com/')

# Configurar la moneda por defecto
CURRENCY = 'cop'  # Peso colombiano

# Configurar los métodos de pago disponibles
PAYMENT_METHODS = [
    'card',  # Tarjeta de crédito/débito
    'transfer',  # Transferencia bancaria
]

# Configurar los estados de pago
PAYMENT_STATUS = {
    'PENDING': 'pendiente',
    'PROCESSING': 'procesando',
    'COMPLETED': 'completada',
    'FAILED': 'fallida',
    'REFUNDED': 'reembolsada',
} 
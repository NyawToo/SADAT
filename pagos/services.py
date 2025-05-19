import stripe
from django.conf import settings
from .stripe_config import CURRENCY, DOMAIN, PAYMENT_STATUS
from .models import Transaccion

class StripeService:
    @staticmethod
    def create_payment_intent(transaccion):
        """
        Crea un PaymentIntent en Stripe para la transacción
        """
        try:
            # Convertir el monto a centavos y asegurar el mínimo de 50 centavos
            amount = max(50, int(round(float(transaccion.monto) * 100)))
            
            # Crear el PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=CURRENCY,
                payment_method_types=['card'],
                metadata={
                    'transaccion_id': transaccion.id,
                    'usuario_id': transaccion.usuario.id,
                    'tipo_transaccion': transaccion.tipo_transaccion
                }
            )
            
            # Actualizar la transacción con el ID del PaymentIntent
            transaccion.stripe_payment_intent_id = payment_intent.id
            transaccion.estado = PAYMENT_STATUS['PENDING']
            transaccion.save()
            
            return payment_intent
            
        except stripe.error.StripeError as e:
            # Registrar el error y actualizar la transacción
            transaccion.estado = PAYMENT_STATUS['FAILED']
            transaccion.detalles_pago = {'error': str(e)}
            transaccion.save()
            raise
    
    @staticmethod
    def create_customer(usuario):
        """
        Crea o recupera un cliente en Stripe
        """
        try:
            # Buscar si el usuario ya tiene un cliente en Stripe
            transaccion_existente = Transaccion.objects.filter(
                usuario=usuario,
                stripe_customer_id__isnull=False
            ).first()
            
            if transaccion_existente and transaccion_existente.stripe_customer_id:
                return transaccion_existente.stripe_customer_id
            
            # Crear un nuevo cliente en Stripe
            customer = stripe.Customer.create(
                email=usuario.email,
                name=f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username,
                metadata={
                    'usuario_id': usuario.id,
                    'username': usuario.username
                }
            )
            
            return customer.id
            
        except stripe.error.StripeError as e:
            # Registrar el error
            print(f"Error al crear cliente en Stripe: {str(e)}")
            return None
    
    @staticmethod
    def create_payment_method(card_data, customer_id=None):
        """
        Crea un método de pago en Stripe
        """
        try:
            # Crear el método de pago
            payment_method = stripe.PaymentMethod.create(
                type='card',
                card=card_data,
                billing_details={
                    'name': card_data.get('name'),
                    'email': card_data.get('email'),
                }
            )
            
            # Si hay un cliente, adjuntar el método de pago al cliente
            if customer_id:
                stripe.PaymentMethod.attach(
                    payment_method.id,
                    customer=customer_id
                )
                
                # Establecer como método de pago predeterminado
                stripe.Customer.modify(
                    customer_id,
                    invoice_settings={
                        'default_payment_method': payment_method.id
                    }
                )
            
            return payment_method.id
            
        except stripe.error.StripeError as e:
            # Registrar el error
            print(f"Error al crear método de pago en Stripe: {str(e)}")
            return None
    
    @staticmethod
    def confirm_payment(transaccion):
        """
        Confirma un pago en Stripe
        """
        try:
            # Confirmar el PaymentIntent
            payment_intent = stripe.PaymentIntent.confirm(
                transaccion.stripe_payment_intent_id
            )
            
            # Actualizar la transacción
            transaccion.estado = PAYMENT_STATUS['COMPLETED']
            transaccion.detalles_pago = {
                'payment_intent': payment_intent.id,
                'status': payment_intent.status,
                'payment_method': payment_intent.payment_method
            }
            transaccion.save()
            
            return payment_intent
            
        except stripe.error.StripeError as e:
            # Registrar el error y actualizar la transacción
            transaccion.estado = PAYMENT_STATUS['FAILED']
            transaccion.detalles_pago = {'error': str(e)}
            transaccion.save()
            raise
    
    @staticmethod
    def create_checkout_session(transaccion, success_url=None, cancel_url=None):
        """
        Crea una sesión de Checkout en Stripe
        """
        try:
            # Convertir el monto a centavos
            amount = int(float(transaccion.monto) * 100)
            
            # URLs de redirección
            if not success_url:
                success_url = "https://sadat-ezff.onrender.com/pagos/confirmar-pago/{transaccion.id}/?success=true"
            if not cancel_url:
                cancel_url = "https://sadat-ezff.onrender.com/pagos/ejecucion-pago/?canceled=true"
            
            # Crear la sesión de Checkout
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': CURRENCY,
                        'unit_amount': amount,
                        'product_data': {
                            'name': f"Pedido #{transaccion.pedido.id if transaccion.pedido else 'Personalizado'}",
                            'description': f"Pago para {transaccion.get_tipo_transaccion_display()}",
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'transaccion_id': transaccion.id,
                    'usuario_id': transaccion.usuario.id,
                    'tipo_transaccion': transaccion.tipo_transaccion
                }
            )
            
            # Actualizar la transacción
            transaccion.stripe_payment_intent_id = session.payment_intent
            transaccion.estado = PAYMENT_STATUS['PENDING']
            transaccion.detalles_pago = {
                'session_id': session.id,
                'payment_intent': session.payment_intent
            }
            transaccion.save()
            
            return session
            
        except stripe.error.StripeError as e:
            # Registrar el error y actualizar la transacción
            transaccion.estado = PAYMENT_STATUS['FAILED']
            transaccion.detalles_pago = {'error': str(e)}
            transaccion.save()
            raise
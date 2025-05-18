from django.urls import path
from . import views

urlpatterns = [
    path('ejecucion-pago/', views.ejecucion_pago, name='ejecucion_pago'),
    path('confirmar-pago/<int:transaccion_id>/', views.confirmar_pago, name='confirmar_pago'),
    path('supervisar-pagos/', views.supervisar_pagos, name='supervisar_pagos'),
    path('recibidos/', views.ver_pagos_recibidos, name='ver_pagos_recibidos'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
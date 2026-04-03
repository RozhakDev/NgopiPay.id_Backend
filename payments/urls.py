from django.urls import path
from .views import PaymenkuWebhookView, CheckPaymentStatusView

urlpatterns = [
    path('webhook/paymenku/', PaymenkuWebhookView.as_view(), name='webhook-paymenku'),

    path('payments/status/<str:reference_id>/', CheckPaymentStatusView.as_view(), name='check-status'),
]
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentWebhookView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('payments/webhook/', PaymentWebhookView.as_view(), name='payment-webhook'),
    path('', include(router.urls)),
]

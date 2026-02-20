from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookEndpointViewSet, WebhookLogListView

router = DefaultRouter()
router.register(r'webhooks', WebhookEndpointViewSet)

urlpatterns = [
    path('webhooks/logs/', WebhookLogListView.as_view(), name='webhook-logs'),
    path('', include(router.urls)),
]

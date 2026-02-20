from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryAttemptViewSet, ProofUploadView

router = DefaultRouter()
router.register(r'attempts', DeliveryAttemptViewSet)

urlpatterns = [
    path('upload/delivery-proof/', ProofUploadView.as_view(), name='proof-upload'),
    path('shipments/<uuid:pk>/upload-proof/', ProofUploadView.as_view(), name='shipment-proof-upload'),
    path('', include(router.urls)),
]

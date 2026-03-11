from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeliveryAttemptViewSet, ProofUploadView, DeliveryConfigViewSet,
    ItemRequestViewSet,
)

router = DefaultRouter()
router.register(r'attempts', DeliveryAttemptViewSet)
router.register(r'delivery-config', DeliveryConfigViewSet)
router.register(r'item-requests', ItemRequestViewSet)

urlpatterns = [
    path(
        'attempts/<uuid:attempt_id>/upload-proof/',
        ProofUploadView.as_view(),
        name='attempt-proof-upload',
    ),
    path('', include(router.urls)),
]

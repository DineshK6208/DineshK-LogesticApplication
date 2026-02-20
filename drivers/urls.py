from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, DriverLocationView, KYCUploadView

router = DefaultRouter()
router.register(r'drivers', DriverViewSet)

urlpatterns = [
    path('drivers/<uuid:pk>/location/', DriverLocationView.as_view(), name='driver-location'),
    path('upload/kyc-document/', KYCUploadView.as_view(), name='kyc-upload'),
    path('', include(router.urls)),
]

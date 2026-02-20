from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShipmentViewSet, ParcelViewSet, RateCalculateView, ShipmentExportView

router = DefaultRouter()
router.register(r'shipments', ShipmentViewSet)
router.register(r'parcels', ParcelViewSet)

urlpatterns = [
    path('shipments/calculate-rate/', RateCalculateView.as_view(), name='shipment-rate-calc'),
    path('shipments/export/', ShipmentExportView.as_view(), name='shipment-export'),
    path('', include(router.urls)),
]

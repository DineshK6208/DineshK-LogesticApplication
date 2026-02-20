from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EarningViewSet, PayoutViewSet, SettlementReportView

router = DefaultRouter()
router.register(r'earnings', EarningViewSet)
router.register(r'payouts', PayoutViewSet)

urlpatterns = [
    path('finance/settlement-report/', SettlementReportView.as_view(), name='settlement-report'),
    path('', include(router.urls)),
]

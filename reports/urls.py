from django.urls import path
from .views import DashboardSummaryView, ShipmentReportView, RevenueReportView

urlpatterns = [
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('reports/shipments/', ShipmentReportView.as_view(), name='report-shipments'),
    path('reports/revenue/', RevenueReportView.as_view(), name='report-revenue'),
]

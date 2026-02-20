from django.urls import path
from .views import PublicTrackView, LiveLocationView

urlpatterns = [
    path('public/track/<str:tracking_number>/', PublicTrackView.as_view(), name='public-track'),
    path('shipments/<uuid:pk>/live-location/', LiveLocationView.as_view(), name='shipment-live-location'),
]

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import TrackingEvent
from .serializers import TrackingEventSerializer
from shipments.models import Shipment


class PublicTrackView(generics.RetrieveAPIView):
    """GET /api/public/track/{trackingNumber}/ — Public tracking API."""
    permission_classes = [AllowAny]
    lookup_field = 'tracking_number'
    queryset = Shipment.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        events = instance.tracking_events.all()
        serializer = TrackingEventSerializer(events, many=True)
        return Response({
            "tracking_number": instance.tracking_number,
            "current_status": instance.status,
            "timeline": serializer.data
        })


class LiveLocationView(generics.RetrieveAPIView):
    """GET /api/shipments/{id}/live-location/ — Real-time tracking."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        shipment_id = self.kwargs.get('pk')
        # In a real app, find driver for this shipment and get latest location
        return Response({
            "shipment_id": shipment_id,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "last_updated": "2024-05-20T10:00:00Z"
        })

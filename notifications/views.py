from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer, SendNotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    """GET /api/notifications/ — Notification management."""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=['patch'])
    def read(self, request, pk=None):
        """PATCH /api/notifications/{id}/read/ — Mark as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(self.get_serializer(notification).data)


class SendNotificationView(generics.CreateAPIView):
    """POST /api/notifications/send/ — Driver Mobile send notification API."""
    serializer_class = SendNotificationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # In a real app, trigger Email/SMS/Push
        from .models import Notification
        Notification.objects.create(
            user_id=serializer.validated_data['user_id'],
            title=serializer.validated_data['title'],
            message=serializer.validated_data['message'],
            notification_type=serializer.validated_data.get('type', 'general')
        )
        return Response({"status": "Notification sent"}, status=status.HTTP_201_CREATED)

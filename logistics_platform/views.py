from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    Overview of available API endpoints.
    """
    return Response({
        'admin': request.build_absolute_uri('/admin/'),
        'accounts': reverse('user-list', request=request, format=format) if 'accounts.urls' in str(request.resolver_match) else '/api/accounts/',
        'webhooks': {
            'logs': reverse('webhook-logs', request=request, format=format),
            'received': reverse('webhook-received', request=request, format=format),
            'payment': reverse('webhook-payment', request=request, format=format),
            'shipment': reverse('webhook-shipment', request=request, format=format),
            'retry': reverse('webhook-retry', request=request, format=format),
        },
        'status': 'Logistics Platform API is running.'
    })

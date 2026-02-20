from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('tenants.urls')),
    path('api/', include('drivers.urls')),
    path('api/', include('vehicles.urls')),
    path('api/', include('shipments.urls')),
    path('api/', include('tracking.urls')),
    path('api/', include('deliveries.urls')),
    path('api/', include('payments.urls')),
    path('api/', include('wallet.urls')),
    path('api/', include('earnings.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('webhooks.urls')),
    path('api/', include('auditlogs.urls')),
    path('api/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

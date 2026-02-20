from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """
    Extracts X-Tenant-ID header and attaches the tenant to the request.
    """

    def process_request(self, request):
        from tenants.models import Tenant
        tenant_id = request.META.get('HTTP_X_TENANT_ID')
        if tenant_id:
            try:
                request.tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Exception:
                request.tenant = None
        else:
            request.tenant = None

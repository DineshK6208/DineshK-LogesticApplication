from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    """Allow access only to super-admin users or superusers."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'super_admin' or request.user.is_superuser)
        )


class IsTenantAdmin(BasePermission):
    """Allow access only to tenant-admin users or superusers."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role in ('super_admin', 'tenant_admin') or request.user.is_superuser)
        )


class IsOperationsManager(BasePermission):
    """Allow access to operations managers and above."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role in ('super_admin', 'tenant_admin', 'operations_manager') or request.user.is_superuser)
        )


class IsDriver(BasePermission):
    """Allow access only to driver users."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role == 'driver' or request.user.is_superuser)
        )


class IsFinanceManager(BasePermission):
    """Allow access to finance managers and above."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role in ('super_admin', 'tenant_admin', 'finance_manager') or request.user.is_superuser)
        )


class IsDriverOrAdmin(BasePermission):
    """Allow access to drivers OR admin roles."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.role in ('super_admin', 'tenant_admin', 'operations_manager', 'driver') or request.user.is_superuser)
        )

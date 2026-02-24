from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Role


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'tenant', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'tenant')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-date_joined',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Logistics Info', {'fields': ('phone', 'role', 'tenant')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('name',)

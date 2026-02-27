import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistics_platform.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

def check_user(email, password):
    print(f"\n--- Checking {email} ---")
    try:
        user = User.objects.get(email=email)
        print(f"User exists in DB: Yes (ID: {user.id})")
        print(f"Is Staff: {user.is_staff}")
        print(f"Is Active: {user.is_active}")
        print(f"Is Superuser: {user.is_superuser}")
        
        # Test authentication with email=
        auth_email = authenticate(email=email, password=password)
        print(f"Auth with email='{email}': {'SUCCESS' if auth_email else 'FAILED'}")
        
        # Test authentication with username=
        auth_username = authenticate(username=email, password=password)
        print(f"Auth with username='{email}': {'SUCCESS' if auth_username else 'FAILED'}")
            
    except User.DoesNotExist:
        print(f"User exists in DB: NO")

# Create a foolproof account
u, _ = User.objects.update_or_create(email='admin@admin.com', defaults={'is_staff': True, 'is_superuser': True, 'role': 'super_admin', 'is_active': True})
u.set_password('admin123')
u.save()
print("\nCreated foolproof user: admin@admin.com / admin123")

check_user('admin@admin.com', 'admin123')
check_user('admin@logistics.com', 'Admin@123')

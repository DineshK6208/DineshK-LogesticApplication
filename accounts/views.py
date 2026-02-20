from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from core.permissions import IsTenantAdmin
from .models import User, Role
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    RoleSerializer,
)


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — Register a new user."""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if request.tenant:
            user.tenant = request.tenant
            user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """POST /api/auth/login/ — Login and get JWT tokens."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class LogoutView(generics.GenericAPIView):
    """POST /api/auth/logout/ — Blacklist the refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """GET/POST /api/users/ — User management (Tenant Admin+)."""
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filterset_fields = ['role', 'is_active']
    search_fields = ['email', 'username']
    ordering_fields = ['date_joined', 'email']

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs


class RoleViewSet(viewsets.ModelViewSet):
    """GET/POST /api/roles/ — Role management (Tenant Admin+)."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        if hasattr(self.request, 'tenant') and self.request.tenant:
            qs = qs.filter(tenant=self.request.tenant)
        return qs

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'], # Use email as username for Django compatibility
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', 'customer'),
            password=validated_data['password'],
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated.")
        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'role', 'tenant', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['phone', 'role', 'is_active']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'tenant', 'permissions', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_permissions(self, value):
        if not value:
            raise serializers.ValidationError("Role must have at least one permission.")
        return value

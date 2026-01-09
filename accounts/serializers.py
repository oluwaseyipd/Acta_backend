"""
Serializers for user authentication and profiles.
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile, UserRole

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords don't match."
            })
        return attrs

    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom claims
        data['user'] = {
            'id': str(self.user.id),
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'full_name': self.user.full_name,
        }

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token
        token['email'] = user.email
        token['full_name'] = user.full_name

        return token


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""

    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    initials = serializers.CharField(source='user.get_initials', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'email', 'first_name', 'last_name', 'full_name', 'initials',
            'phone_number', 'bio', 'location', 'birth_date', 'avatar', 'website',
            'timezone', 'notification_preferences',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def update(self, instance, validated_data):
        """Update profile and nested user fields."""
        user_data = validated_data.pop('user', {})

        # Update user fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for references."""

    full_name = serializers.CharField(read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    avatar = serializers.ImageField(source='profile.avatar', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'initials', 'avatar']
        read_only_fields = fields


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords don't match."
            })
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            # Don't reveal if email exists for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""

    token = serializers.CharField()
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords don't match."
            })
        return attrs

"""
Views for user authentication and profiles.
"""
from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import Profile
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from core.permissions import IsProfileOwnerOrReadOnly

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """User registration endpoint."""

    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        # Trigger welcome email asynchronously
        from django.db import transaction
        from .tasks import send_welcome_email
        try:
            transaction.on_commit(lambda: send_welcome_email.delay(str(user.id)))
        except Exception:
            pass

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom login endpoint with additional user data."""

    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """Logout endpoint - blacklist refresh token."""

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get and update current user's profile."""

    serializer_class = ProfileSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerOrReadOnly]

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(generics.UpdateAPIView):
    """Change user password."""

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': 'Password changed successfully'})


class PasswordResetRequestView(generics.CreateAPIView):
    """Request password reset email."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email__iexact=email).first()
        if user:
            from django.contrib.auth.tokens import default_token_generator as password_reset_token_generator
            from .models import PasswordResetToken
            from .tasks import send_password_reset_email
            from django.db import transaction

            token = password_reset_token_generator.make_token(user)
            PasswordResetToken.objects.create(user=user, token=token)
            
            try:
                transaction.on_commit(lambda: send_password_reset_email.delay(str(user.id), token))
            except Exception:
                pass

        return Response({
            'message': 'If an account exists with this email, a reset link will be sent.'
        })


class PasswordResetConfirmView(generics.CreateAPIView):
    """Confirm password reset with token."""

    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        from django.contrib.auth.tokens import default_token_generator as password_reset_token_generator
        from .models import PasswordResetToken
        from .tasks import send_password_changed_email
        from django.db import transaction

        reset_record = PasswordResetToken.objects.filter(token=token, used=False).first()

        if not reset_record:
            return Response({"detail": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        if reset_record.is_expired() or not password_reset_token_generator.check_token(reset_record.user, token):
            return Response({"detail": "Invalid or expired reset token."}, status=status.HTTP_400_BAD_REQUEST)

        user = reset_record.user
        user.set_password(new_password)
        user.save()

        reset_record.used = True
        reset_record.save()

        try:
            transaction.on_commit(lambda: send_password_changed_email.delay(str(user.id)))
        except Exception:
            pass

        return Response({'message': 'Password reset successful'})


class CurrentUserView(generics.RetrieveAPIView):
    """Get current authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GoogleAuthUrlView(APIView):
    """View to get the Google OAuth2 authorization URL."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        from django.conf import settings
        import urllib.parse
        
        client_id = settings.GOOGLE_CLIENT_ID
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        
        url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
        return Response({"url": url})


class GoogleAuthCallbackView(APIView):
    """View to handle the Google OAuth2 callback code exchange and login/registration."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from django.conf import settings
        from django.db import transaction
        from rest_framework_simplejwt.tokens import RefreshToken
        import requests
        
        code = request.data.get("code")
        if not code:
            return Response(
                {"detail": "Authorization code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Exchange code for Google tokens
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        try:
            token_response = requests.post(token_url, data=payload, timeout=10)
            if not token_response.ok:
                return Response(
                    {"detail": f"Failed to exchange Google authorization code: {token_response.text}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            tokens = token_response.json()
            id_token_str = tokens.get("id_token")
            if not id_token_str:
                return Response(
                    {"detail": "Google did not return an ID token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except requests.RequestException as e:
            return Response(
                {"detail": f"Network error connecting to Google: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Verify Google ID token using Google API tokeninfo endpoint
        try:
            info_response = requests.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": id_token_str},
                timeout=10
            )
            if not info_response.ok:
                return Response(
                    {"detail": f"Failed to verify ID token: {info_response.text}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            id_info = info_response.json()
            
            # Basic issuer validation
            if id_info.get("iss") not in ["accounts.google.com", "https://accounts.google.com"]:
                return Response(
                    {"detail": "Invalid issuer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Audience validation
            if id_info.get("aud") != settings.GOOGLE_CLIENT_ID:
                return Response(
                    {"detail": "Audience mismatch."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except requests.RequestException as e:
            return Response(
                {"detail": f"Network error verifying ID token: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY
            )

        email = id_info.get("email")
        if not email:
            return Response(
                {"detail": "Email is missing from Google account info."},
                status=status.HTTP_400_BAD_REQUEST
            )

        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        # Find or create user
        user = User.objects.filter(email__iexact=email).first()
        is_new_user = False

        if not user:
            is_new_user = True
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=None
                )
            
            # Send welcome email on transaction commit
            from .tasks import send_welcome_email
            try:
                transaction.on_commit(lambda: send_welcome_email.delay(str(user.id)))
            except Exception:
                pass

        # Generate simplejwt tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "registered": True,
            "is_new": is_new_user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": UserSerializer(user).data,
            "message": "Google login successful"
        }, status=status.HTTP_200_OK)


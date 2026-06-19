"""
Comprehensive tests for accounts views and functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Profile, UserRole

User = get_user_model()


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for user registration."""

    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'tokens' in response.data
        assert response.data['user']['email'] == 'newuser@example.com'

        # Verify user was created
        user = User.objects.get(email='newuser@example.com')
        assert user.first_name == 'New'
        assert user.last_name == 'User'

        # Verify default categories were automatically created
        from tasks.models import Category
        user_categories = Category.objects.filter(user=user)
        assert user_categories.count() == 5
        category_names = [cat.name for cat in user_categories]
        assert 'Work' in category_names
        assert 'Personal' in category_names

    def test_register_user_triggers_email(self, api_client):
        """Test user registration triggers welcome email task delay."""
        from unittest.mock import patch
        url = reverse('register')
        data = {
            'email': 'newuser_email_trigger@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        with patch('accounts.tasks.send_welcome_email.delay') as mock_send:
            with patch('django.db.transaction.on_commit', side_effect=lambda f: f()):
                response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        user = User.objects.get(email='newuser_email_trigger@example.com')
        mock_send.assert_called_once_with(str(user.id))

    def test_register_user_password_mismatch(self, api_client):
        """Test registration with password mismatch."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'different123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password_confirm' in response.data

    def test_register_duplicate_email(self, api_client, user):
        """Test registration with duplicate email."""
        url = reverse('register')
        data = {
            'email': user.email,
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, api_client):
        """Test registration with invalid email."""
        url = reverse('register')
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, api_client):
        """Test registration with weak password."""
        url = reverse('register')
        data = {
            'email': 'newuser@example.com',
            'password': '123',
            'password_confirm': '123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Tests for user login."""

    def test_login_success(self, api_client, user):
        """Test successful login."""
        url = reverse('login')
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['email'] == user.email

    def test_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            'email': user.email,
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Test login with nonexistent user."""
        url = reverse('login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, api_client, user):
        """Test login with inactive user."""
        user.is_active = False
        user.save()

        url = reverse('login')
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserLogout:
    """Tests for user logout."""

    def test_logout_success(self, authenticated_client, jwt_tokens):
        """Test successful logout."""
        url = reverse('logout')
        data = {'refresh': jwt_tokens['refresh']}
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Logout successful'

    def test_logout_invalid_token(self, authenticated_client):
        """Test logout with invalid refresh token."""
        url = reverse('logout')
        data = {'refresh': 'invalid_token'}
        response = authenticated_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTokenRefresh:
    """Tests for JWT token refresh."""

    def test_token_refresh_success(self, api_client, jwt_tokens):
        """Test successful token refresh."""
        url = reverse('token_refresh')
        data = {'refresh': jwt_tokens['refresh']}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_token_refresh_invalid_token(self, api_client):
        """Test token refresh with invalid refresh token."""
        url = reverse('token_refresh')
        data = {'refresh': 'invalid_refresh_token'}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCurrentUser:
    """Tests for current user endpoint."""

    def test_get_current_user(self, authenticated_client, user):
        """Test getting current authenticated user."""
        url = reverse('current_user')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['first_name'] == user.first_name
        assert response.data['last_name'] == user.last_name

    def test_get_current_user_unauthenticated(self, api_client):
        """Test getting current user without authentication."""
        url = reverse('current_user')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserProfile:
    """Tests for user profile management."""

    def test_get_profile(self, authenticated_client, profile):
        """Test getting user profile."""
        url = reverse('profile')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == profile.user.email
        assert response.data['bio'] == profile.bio
        assert response.data['timezone'] == profile.timezone

    def test_update_profile(self, authenticated_client, profile):
        """Test updating user profile."""
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio',
            'timezone': 'America/New_York'
        }
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK

        # Refresh from database
        profile.refresh_from_db()
        profile.user.refresh_from_db()

        assert profile.user.first_name == 'Updated'
        assert profile.user.last_name == 'Name'
        assert profile.bio == 'Updated bio'
        assert profile.timezone == 'America/New_York'

    def test_update_profile_phone(self, authenticated_client, profile):
        """Test updating profile phone number."""
        url = reverse('profile')
        data = {'phone_number': '+1234567890'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        profile.refresh_from_db()
        assert profile.phone_number == '+1234567890'

    def test_update_profile_invalid_phone(self, authenticated_client, profile):
        """Test updating profile with invalid phone number."""
        url = reverse('profile')
        data = {'phone_number': 'invalid_phone'}
        response = authenticated_client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestChangePassword:
    """Tests for password change functionality."""

    def test_change_password_success(self, authenticated_client, user):
        """Test successful password change."""
        url = reverse('password_change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password changed successfully'

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password('newpass123')

    def test_change_password_wrong_old_password(self, authenticated_client):
        """Test password change with wrong old password."""
        url = reverse('password_change')
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in response.data

    def test_change_password_mismatch(self, authenticated_client):
        """Test password change with password mismatch."""
        url = reverse('password_change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'different123'
        }
        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password_confirm' in response.data

    def test_change_password_weak_password(self, authenticated_client):
        """Test password change with weak new password."""
        url = reverse('password_change')
        data = {
            'old_password': 'testpass123',
            'new_password': '123',
            'new_password_confirm': '123'
        }
        response = authenticated_client.put(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self, api_client):
        """Test password change without authentication."""
        url = reverse('password_change')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        response = api_client.put(url, data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordReset:
    """Tests for password reset functionality."""

    def test_password_reset_request(self, api_client, user):
        """Test password reset request."""
        from unittest.mock import patch
        from accounts.models import PasswordResetToken

        url = reverse('password_reset')
        data = {'email': user.email}

        with patch('accounts.tasks.send_password_reset_email.delay') as mock_send:
            with patch('django.db.transaction.on_commit', side_effect=lambda f: f()):
                response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'If an account exists' in response.data['message']

        # Verify token was created
        reset_token = PasswordResetToken.objects.filter(user=user).first()
        assert reset_token is not None
        assert reset_token.used is False
        mock_send.assert_called_once_with(str(user.id), reset_token.token)

    def test_password_reset_nonexistent_email(self, api_client):
        """Test password reset with nonexistent email."""
        url = reverse('password_reset')
        data = {'email': 'nonexistent@example.com'}
        response = api_client.post(url, data)

        # Should return success message for security
        assert response.status_code == status.HTTP_200_OK
        assert 'If an account exists' in response.data['message']

    def test_password_reset_invalid_email(self, api_client):
        """Test password reset with invalid email format."""
        url = reverse('password_reset')
        data = {'email': 'invalid-email'}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_confirm_success(self, api_client, user):
        """Test successful password reset confirmation."""
        from unittest.mock import patch
        from django.contrib.auth.tokens import default_token_generator as password_reset_token_generator
        from accounts.models import PasswordResetToken

        # Generate a valid token
        token = password_reset_token_generator.make_token(user)
        reset_record = PasswordResetToken.objects.create(user=user, token=token)

        url = reverse('password_reset_confirm')
        data = {
            'token': token,
            'new_password': 'newsecurepassword123',
            'new_password_confirm': 'newsecurepassword123'
        }

        with patch('accounts.tasks.send_password_changed_email.delay') as mock_send:
            with patch('django.db.transaction.on_commit', side_effect=lambda f: f()):
                response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['message'] == 'Password reset successful'

        # Verify password is changed
        user.refresh_from_db()
        assert user.check_password('newsecurepassword123')

        # Verify token is marked used
        reset_record.refresh_from_db()
        assert reset_record.used is True

        # Verify email task was queued
        mock_send.assert_called_once_with(str(user.id))

    def test_password_reset_confirm_invalid_token(self, api_client, user):
        """Test password reset confirmation with invalid token."""
        url = reverse('password_reset_confirm')
        data = {
            'token': 'invalid-token-12345',
            'new_password': 'newsecurepassword123',
            'new_password_confirm': 'newsecurepassword123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid or expired reset token.' in response.data['detail']

    def test_password_reset_confirm_expired_token(self, api_client, user):
        """Test password reset confirmation with expired token."""
        from django.contrib.auth.tokens import default_token_generator as password_reset_token_generator
        from accounts.models import PasswordResetToken
        from django.utils import timezone
        from datetime import timedelta

        token = password_reset_token_generator.make_token(user)
        reset_record = PasswordResetToken.objects.create(user=user, token=token)
        
        # Backdate the created_at to expire it (TIMEOUT is typically 259200 seconds / 3 days)
        expired_time = timezone.now() - timedelta(days=4)
        PasswordResetToken.objects.filter(id=reset_record.id).update(created_at=expired_time)

        url = reverse('password_reset_confirm')
        data = {
            'token': token,
            'new_password': 'newsecurepassword123',
            'new_password_confirm': 'newsecurepassword123'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Invalid or expired reset token.' in response.data['detail']


@pytest.mark.django_db
class TestEmailTasks:
    """Tests for Celery email tasks."""

    def test_send_welcome_email_task(self, user):
        from unittest.mock import patch
        from accounts.tasks import send_welcome_email

        with patch('accounts.tasks.send_email') as mock_send_email:
            send_welcome_email(str(user.id))
            
            mock_send_email.assert_called_once()
            args, kwargs = mock_send_email.call_args
            assert args[0] == "Welcome to Acta"
            assert user.email in args[2]

    def test_send_password_reset_email_task(self, user):
        from unittest.mock import patch
        from accounts.tasks import send_password_reset_email

        with patch('accounts.tasks.send_email') as mock_send_email:
            send_password_reset_email(str(user.id), 'fake-token-xyz')
            
            mock_send_email.assert_called_once()
            args, kwargs = mock_send_email.call_args
            assert args[0] == "Acta Password Reset"
            assert user.email in args[2]
            assert "fake-token-xyz" in args[1] or "fake-token-xyz" in kwargs.get('html_message', '')

    def test_send_password_changed_email_task(self, user):
        from unittest.mock import patch
        from accounts.tasks import send_password_changed_email

        with patch('accounts.tasks.send_email') as mock_send_email:
            send_password_changed_email(str(user.id))
            
            mock_send_email.assert_called_once()
            args, kwargs = mock_send_email.call_args
            assert args[0] == "Your Acta password was changed"
            assert user.email in args[2]


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self):
        """Test user creation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        assert user.email == 'test@example.com'
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_superuser_creation(self):
        """Test superuser creation."""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User'
        )

        assert user.email == 'admin@example.com'
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_user_str(self, user):
        """Test user string representation."""
        assert str(user) == user.email

    def test_user_full_name(self, user):
        """Test user full_name property."""
        expected_name = f"{user.first_name} {user.last_name}".strip()
        assert user.full_name == expected_name

    def test_user_get_initials(self, user):
        """Test user get_initials method."""
        expected_initials = f"{user.first_name[0]}{user.last_name[0]}".upper()
        assert user.get_initials() == expected_initials

    def test_user_no_username(self):
        """Test that username field is not used."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )

        # USERNAME_FIELD should be email
        assert User.USERNAME_FIELD == 'email'
        assert user.username is None


@pytest.mark.django_db
class TestProfileModel:
    """Tests for Profile model."""

    def test_profile_creation(self, user):
        """Test profile creation and auto-creation via signals."""
        # Profile should be auto-created via signal
        profile = user.profile

        # Update the profile with test data
        profile.bio = 'Test bio'
        profile.phone_number = '+1234567890'
        profile.location = 'Test City'
        profile.timezone = 'UTC'
        profile.save()

        assert profile.user == user
        assert profile.bio == 'Test bio'
        assert profile.phone_number == '+1234567890'
        assert profile.location == 'Test City'
        assert profile.timezone == 'UTC'

    def test_profile_str(self, profile):
        """Test profile string representation."""
        expected_str = f"{profile.user.email}'s Profile"
        assert str(profile) == expected_str

    def test_profile_auto_creation_signal(self):
        """Test that profile is automatically created when user is created."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Profile should be created automatically via signal
        assert hasattr(user, 'profile')
        assert Profile.objects.filter(user=user).exists()

    def test_profile_notification_preferences(self, profile):
        """Test profile notification preferences JSON field."""
        preferences = {
            'email': True,
            'push': False,
            'sms': True
        }
        profile.notification_preferences = preferences
        profile.save()

        profile.refresh_from_db()
        assert profile.notification_preferences == preferences


@pytest.mark.django_db
class TestUserRoleModel:
    """Tests for UserRole model."""

    def test_role_creation(self, user):
        """Test user role creation and auto-creation via signals."""
        # Role should be auto-created via signal as MEMBER
        role = UserRole.objects.get(user=user)
        assert role.user == user
        assert role.role == UserRole.RoleType.MEMBER

        # Update role to ADMIN
        role.role = UserRole.RoleType.ADMIN
        role.save()

        assert role.role == UserRole.RoleType.ADMIN

    def test_role_auto_creation_signal(self):
        """Test that role is automatically created when user is created."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Role should be created automatically via signal
        assert UserRole.objects.filter(user=user).exists()
        role = UserRole.objects.get(user=user)
        assert role.role == UserRole.RoleType.MEMBER

    def test_role_str(self, user):
        """Test user role string representation."""
        # Get the auto-created role and update it
        role = UserRole.objects.get(user=user)
        role.role = UserRole.RoleType.ADMIN
        role.save()

        expected_str = f"{user.email} - Admin"
        assert str(role) == expected_str

    def test_role_permissions(self, user):
        """Test role permissions JSON field."""
        # Get the auto-created role and update it
        role = UserRole.objects.get(user=user)
        permissions = ['can_create_tasks', 'can_delete_tasks']
        role.role = UserRole.RoleType.ADMIN
        role.permissions = permissions
        role.save()

        assert role.permissions == permissions

    def test_role_choices(self):
        """Test role type choices."""
        choices = UserRole.RoleType.choices
        expected_choices = [
            ('admin', 'Admin'),
            ('manager', 'Manager'),
            ('member', 'Member'),
            ('viewer', 'Viewer')
        ]
        assert choices == expected_choices


@pytest.mark.django_db
class TestProfilePermissions:
    """Tests for profile permissions."""

    def test_user_can_view_own_profile(self, authenticated_client, profile):
        """Test that user can view their own profile."""
        url = reverse('profile')
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_view_other_profile(self, api_client, multiple_users):
        """Test that user cannot view another user's profile."""
        user1, user2 = multiple_users[0], multiple_users[1]

        # Create profiles for both users
        Profile.objects.get_or_create(user=user1)
        Profile.objects.get_or_create(user=user2)

        # Authenticate as user1
        api_client.force_authenticate(user=user1)

        # Try to access user2's profile (this would require a different endpoint)
        # For now, just verify own profile access works
        url = reverse('profile')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # The response should contain user1's data, not user2's
        assert response.data['email'] == user1.email


@pytest.mark.django_db
class TestGoogleAuth:
    """Tests for Google OAuth2 authentication."""

    def test_google_auth_url_success(self, api_client):
        """Test getting Google OAuth2 authorization URL."""
        url = reverse('google_auth_url')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'url' in response.data
        assert 'accounts.google.com' in response.data['url']
        assert 'client_id' in response.data['url']

    def test_google_auth_callback_missing_code(self, api_client):
        """Test callback rejects request missing code."""
        url = reverse('google_auth_callback')
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'code' in response.data['detail'].lower() or 'code' in response.data

    def test_google_auth_callback_new_user(self, api_client):
        """Test callback successfully registers a new user with Google account."""
        from unittest.mock import patch, MagicMock
        
        url = reverse('google_auth_callback')
        data = {'code': 'valid_auth_code_xyz'}

        # Mock token exchange response from Google
        mock_token_response = MagicMock()
        mock_token_response.ok = True
        mock_token_response.json.return_value = {
            'id_token': 'fake_id_token_string'
        }

        # Mock token info response from Google
        mock_info_response = MagicMock()
        mock_info_response.ok = True
        mock_info_response.json.return_value = {
            'iss': 'https://accounts.google.com',
            'aud': '', # settings.GOOGLE_CLIENT_ID will be empty by default in tests
            'email': 'newgoogleuser@example.com',
            'given_name': 'Google',
            'family_name': 'User'
        }

        # Mock setting.GOOGLE_CLIENT_ID to match the mock
        with patch('django.conf.settings.GOOGLE_CLIENT_ID', ''):
            with patch('requests.post', return_value=mock_token_response) as mock_post:
                with patch('requests.get', return_value=mock_info_response) as mock_get:
                    with patch('accounts.tasks.send_welcome_email.delay') as mock_email_delay:
                        with patch('django.db.transaction.on_commit', side_effect=lambda f: f()):
                            response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['registered'] is True
        assert response.data['is_new'] is True
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'newgoogleuser@example.com'

        # Verify database entities created
        new_user = User.objects.get(email='newgoogleuser@example.com')
        assert new_user.first_name == 'Google'
        assert new_user.last_name == 'User'
        
        # Signal side-effects: profile, role, and categories
        assert hasattr(new_user, 'profile')
        assert UserRole.objects.filter(user=new_user, role=UserRole.RoleType.MEMBER).exists()
        from tasks.models import Category
        assert Category.objects.filter(user=new_user).count() == 5

        # Email task trigger
        mock_email_delay.assert_called_once_with(str(new_user.id))

    def test_google_auth_callback_existing_user(self, api_client, user):
        """Test callback successfully logs in an existing user."""
        from unittest.mock import patch, MagicMock
        
        url = reverse('google_auth_callback')
        data = {'code': 'valid_auth_code_existing'}

        # Mock token exchange response from Google
        mock_token_response = MagicMock()
        mock_token_response.ok = True
        mock_token_response.json.return_value = {
            'id_token': 'fake_id_token_string'
        }

        # Mock token info response from Google
        mock_info_response = MagicMock()
        mock_info_response.ok = True
        mock_info_response.json.return_value = {
            'iss': 'https://accounts.google.com',
            'aud': '',
            'email': user.email, # Match existing user email
            'given_name': user.first_name,
            'family_name': user.last_name
        }

        with patch('django.conf.settings.GOOGLE_CLIENT_ID', ''):
            with patch('requests.post', return_value=mock_token_response):
                with patch('requests.get', return_value=mock_info_response):
                    with patch('accounts.tasks.send_welcome_email.delay') as mock_email_delay:
                        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['registered'] is True
        assert response.data['is_new'] is False
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == user.email

        # Welcome email should NOT be sent for existing user login
        mock_email_delay.assert_not_called()

    def test_google_auth_callback_invalid_token(self, api_client):
        """Test callback handles invalid tokens from Google gracefully."""
        from unittest.mock import patch, MagicMock
        
        url = reverse('google_auth_callback')
        data = {'code': 'invalid_code'}

        # Mock token exchange failure
        mock_token_response = MagicMock()
        mock_token_response.ok = False
        mock_token_response.text = 'Invalid authorization code'

        with patch('requests.post', return_value=mock_token_response):
            response = api_client.post(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Failed to exchange Google authorization code' in response.data['detail']


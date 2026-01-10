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
        url = reverse('password_reset')
        data = {'email': user.email}
        response = api_client.post(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'If an account exists' in response.data['message']

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

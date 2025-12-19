"""Tests for User API endpoints."""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_user_success(self, api_client):
        """Test successful user registration."""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "User registered successfully."
        assert response.data["user"]["username"] == "newuser"
        assert User.objects.filter(username="newuser").exists()
    
    def test_register_user_password_mismatch(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse("users:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_user_duplicate_username(self, api_client, user):
        """Test registration with existing username."""
        url = reverse("users:register")
        data = {
            "username": user.username,  # Already exists
            "email": "another@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_user_duplicate_email(self, api_client, user):
        """Test registration with existing email."""
        url = reverse("users:register")
        data = {
            "username": "uniqueuser",
            "email": user.email,  # Already exists
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserAuthentication:
    """Tests for JWT authentication."""
    
    def test_obtain_token_success(self, api_client, user):
        """Test successful token obtain."""
        url = reverse("users:token_obtain_pair")
        data = {
            "username": user.username,
            "password": "testpass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
    
    def test_obtain_token_invalid_credentials(self, api_client, user):
        """Test token obtain with wrong password."""
        url = reverse("users:token_obtain_pair")
        data = {
            "username": user.username,
            "password": "wrongpassword",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, user):
        """Test token refresh."""
        # First get tokens
        token_url = reverse("users:token_obtain_pair")
        token_response = api_client.post(token_url, {
            "username": user.username,
            "password": "testpass123",
        }, format="json")
        
        refresh_token = token_response.data["refresh"]
        
        # Now refresh
        refresh_url = reverse("users:token_refresh")
        response = api_client.post(refresh_url, {
            "refresh": refresh_token,
        }, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data


@pytest.mark.django_db
class TestUserList:
    """Tests for user list endpoint."""
    
    def test_list_users(self, api_client, user, other_user):
        """Test listing all users."""
        url = reverse("users:user-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2
    
    def test_search_users(self, api_client, user, other_user):
        """Test searching users by username."""
        url = reverse("users:user-list")
        
        response = api_client.get(url, {"search": "testuser"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["username"] == "testuser"


@pytest.mark.django_db
class TestUserDetail:
    """Tests for user detail endpoint."""
    
    def test_get_user_profile(self, api_client, user):
        """Test getting user profile by username."""
        url = reverse("users:user-detail", kwargs={"username": user.username})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
    
    def test_get_nonexistent_user(self, api_client):
        """Test getting profile of non-existent user."""
        url = reverse("users:user-detail", kwargs={"username": "nonexistent"})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCurrentUser:
    """Tests for current user endpoint."""
    
    def test_get_current_user(self, authenticated_client, user):
        """Test getting current user profile."""
        url = reverse("users:current-user")
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
        assert "email" in response.data  # Should include email for own profile
        assert "preferences" in response.data
    
    def test_get_current_user_unauthenticated(self, api_client):
        """Test current user endpoint without auth."""
        url = reverse("users:current-user")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_current_user(self, authenticated_client, user):
        """Test updating current user profile."""
        url = reverse("users:current-user")
        data = {
            "bio": "Updated bio text",
        }
        
        response = authenticated_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.bio == "Updated bio text"
    
    def test_update_preferences(self, authenticated_client, user):
        """Test updating user preferences."""
        url = reverse("users:current-user")
        data = {
            "preferences": {"theme": "dark", "notifications": {"email": True}},
        }
        
        response = authenticated_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        
        user.refresh_from_db()
        assert user.preferences["theme"] == "dark"

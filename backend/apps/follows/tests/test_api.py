"""Tests for Follow API endpoints."""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.follows.models import Follow


@pytest.mark.django_db
class TestFollowToggle:
    """Tests for follow toggle endpoint."""
    
    def test_follow_user(self, authenticated_client, user, other_user):
        """Test following a user."""
        url = reverse("follows:follow-toggle", kwargs={"username": other_user.username})
        
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["following"] is True
        assert Follow.objects.filter(follower=user, following=other_user).exists()
    
    def test_unfollow_user(self, authenticated_client, user, other_user):
        """Test unfollowing a user (toggle)."""
        # First follow
        Follow.objects.create(follower=user, following=other_user)
        
        url = reverse("follows:follow-toggle", kwargs={"username": other_user.username})
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["following"] is False
        assert not Follow.objects.filter(follower=user, following=other_user).exists()
    
    def test_cannot_follow_self(self, authenticated_client, user):
        """Test that users cannot follow themselves."""
        url = reverse("follows:follow-toggle", kwargs={"username": user.username})
        
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_follow_unauthenticated(self, api_client, other_user):
        """Test following without authentication."""
        url = reverse("follows:follow-toggle", kwargs={"username": other_user.username})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_follow_nonexistent_user(self, authenticated_client):
        """Test following a non-existent user."""
        url = reverse("follows:follow-toggle", kwargs={"username": "nonexistent"})
        
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFollowersList:
    """Tests for followers list endpoint."""
    
    def test_list_followers(self, api_client, user, other_user):
        """Test listing followers of a user."""
        Follow.objects.create(follower=other_user, following=user)
        
        url = reverse("follows:followers-list", kwargs={"username": user.username})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["user"]["username"] == other_user.username
    
    def test_list_followers_empty(self, api_client, user):
        """Test listing followers when none exist."""
        url = reverse("follows:followers-list", kwargs={"username": user.username})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []


@pytest.mark.django_db
class TestFollowingList:
    """Tests for following list endpoint."""
    
    def test_list_following(self, api_client, user, other_user):
        """Test listing users that a user is following."""
        Follow.objects.create(follower=user, following=other_user)
        
        url = reverse("follows:following-list", kwargs={"username": user.username})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["user"]["username"] == other_user.username
    
    def test_list_following_empty(self, api_client, user):
        """Test listing following when none exist."""
        url = reverse("follows:following-list", kwargs={"username": user.username})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []

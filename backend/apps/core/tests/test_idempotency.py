"""Tests for idempotency functionality."""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.posts.models import Post


@pytest.mark.django_db
class TestIdempotency:
    """Tests for idempotent POST operations."""
    
    def test_create_post_without_idempotency_key(self, authenticated_client, user):
        """Test that posts can be created without idempotency key."""
        url = reverse("posts:post-list")
        data = {"content": "Test post without key"}
        
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(content="Test post without key").exists()
    
    def test_create_post_with_idempotency_key(self, authenticated_client, user):
        """Test that posts can be created with idempotency key."""
        url = reverse("posts:post-list")
        data = {"content": "Test post with key"}
        
        response = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY="unique-key-123",
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(content="Test post with key").count() == 1
    
    def test_idempotent_retry_returns_cached_response(self, authenticated_client, user):
        """Test that retrying with same key returns cached response."""
        url = reverse("posts:post-list")
        data = {"content": "Idempotent post"}
        idempotency_key = "retry-key-456"
        
        # First request
        response1 = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY=idempotency_key,
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        post_id = response1.data["id"]
        
        # Retry with same key - should return cached response
        response2 = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY=idempotency_key,
        )
        
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data["id"] == post_id  # Same post ID
        assert response2.get("X-Idempotent-Replayed") == "true"
        
        # Verify only one post was created
        assert Post.objects.filter(content="Idempotent post").count() == 1
    
    def test_different_idempotency_keys_create_different_posts(self, authenticated_client, user):
        """Test that different keys create different posts."""
        url = reverse("posts:post-list")
        data = {"content": "Post content"}
        
        response1 = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY="key-1",
        )
        
        response2 = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY="key-2",
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        assert response2.status_code == status.HTTP_201_CREATED
        assert response1.data["id"] != response2.data["id"]
        
        # Two posts created
        assert Post.objects.filter(content="Post content").count() == 2
    
    def test_idempotency_key_conflict(self, authenticated_client, user):
        """Test that using same key with different content returns conflict."""
        url = reverse("posts:post-list")
        idempotency_key = "conflict-key-789"
        
        # First request
        response1 = authenticated_client.post(
            url, {"content": "First content"}, format="json",
            HTTP_X_IDEMPOTENCY_KEY=idempotency_key,
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Second request with same key but different content
        response2 = authenticated_client.post(
            url, {"content": "Different content"}, format="json",
            HTTP_X_IDEMPOTENCY_KEY=idempotency_key,
        )
        
        # Should return conflict error
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert response2.data["error"]["code"] == "IDEMPOTENCY_CONFLICT"
    
    def test_idempotent_comment_creation(self, authenticated_client, user, post):
        """Test idempotent comment creation."""
        url = reverse("comments:comment-list", kwargs={"post_id": post.id})
        data = {"content": "Idempotent comment"}
        idempotency_key = "comment-key-123"
        
        # First request
        response1 = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY=idempotency_key,
        )
        
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Retry
        response2 = authenticated_client.post(
            url, data, format="json",
            HTTP_X_IDEMPOTENCY_KEY=idempotency_key,
        )
        
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.data["id"] == response1.data["id"]
        assert response2.get("X-Idempotent-Replayed") == "true"

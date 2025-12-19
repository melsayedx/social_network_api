"""Tests for Post API endpoints."""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.posts.models import Post


@pytest.mark.django_db
class TestPostList:
    """Tests for post list endpoint."""
    
    def test_list_posts_empty(self, api_client):
        """Test listing posts when none exist."""
        url = reverse("posts:post-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []
    
    def test_list_posts(self, api_client, post):
        """Test listing all posts."""
        url = reverse("posts:post-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["content"] == post.content
    
    def test_list_posts_pagination(self, api_client, user):
        """Test post pagination."""
        # Create 25 posts
        for i in range(25):
            Post.objects.create(user=user, content=f"Post {i}")
        
        url = reverse("posts:post-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 20  # Default page size
        assert response.data["count"] == 25
    
    def test_filter_posts_by_user(self, api_client, post, other_user):
        """Test filtering posts by username."""
        # Create post by other user
        Post.objects.create(user=other_user, content="Other user's post")
        
        url = reverse("posts:post-list")
        response = api_client.get(url, {"user__username": post.user.username})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["user"]["username"] == post.user.username
    
    def test_search_posts(self, api_client, user):
        """Test searching posts by content."""
        Post.objects.create(user=user, content="Python is awesome")
        Post.objects.create(user=user, content="JavaScript is cool")
        
        url = reverse("posts:post-list")
        response = api_client.get(url, {"search": "Python"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert "Python" in response.data["results"][0]["content"]


@pytest.mark.django_db
class TestPostCreate:
    """Tests for post creation endpoint."""
    
    def test_create_post_authenticated(self, authenticated_client, user):
        """Test creating a post while authenticated."""
        url = reverse("posts:post-list")
        data = {"content": "This is my new post!"}
        
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["content"] == "This is my new post!"
        assert Post.objects.filter(user=user, content="This is my new post!").exists()
    
    def test_create_post_with_hashtags(self, authenticated_client, user):
        """Test creating a post with hashtags."""
        url = reverse("posts:post-list")
        data = {
            "content": "Learning Django today!",
            "hashtags": ["django", "python", "webdev"],
        }
        
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        
        post = Post.objects.get(user=user, content="Learning Django today!")
        assert post.metadata["hashtags"] == ["django", "python", "webdev"]
    
    def test_create_post_unauthenticated(self, api_client):
        """Test creating a post without authentication."""
        url = reverse("posts:post-list")
        data = {"content": "Anonymous post attempt"}
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_post_empty_content(self, authenticated_client):
        """Test creating a post with empty content."""
        url = reverse("posts:post-list")
        data = {"content": ""}
        
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPostDetail:
    """Tests for post detail endpoint."""
    
    def test_get_post(self, api_client, post):
        """Test getting a single post."""
        url = reverse("posts:post-detail", kwargs={"pk": post.id})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(post.id)
        assert response.data["content"] == post.content
    
    def test_get_nonexistent_post(self, api_client):
        """Test getting a non-existent post."""
        import uuid
        url = reverse("posts:post-detail", kwargs={"pk": uuid.uuid4()})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestPostUpdate:
    """Tests for post update endpoint."""
    
    def test_update_own_post(self, authenticated_client, post):
        """Test updating own post."""
        url = reverse("posts:post-detail", kwargs={"pk": post.id})
        data = {"content": "Updated content"}
        
        response = authenticated_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        
        post.refresh_from_db()
        assert post.content == "Updated content"
        assert post.metadata.get("edited") is True
    
    def test_update_other_user_post(self, authenticated_client, other_user):
        """Test that users cannot update others' posts."""
        other_post = Post.objects.create(user=other_user, content="Other's post")
        url = reverse("posts:post-detail", kwargs={"pk": other_post.id})
        data = {"content": "Hacked content"}
        
        response = authenticated_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPostDelete:
    """Tests for post deletion endpoint."""
    
    def test_delete_own_post(self, authenticated_client, post):
        """Test deleting own post."""
        url = reverse("posts:post-detail", kwargs={"pk": post.id})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(pk=post.id).exists()
    
    def test_delete_other_user_post(self, authenticated_client, other_user):
        """Test that users cannot delete others' posts."""
        other_post = Post.objects.create(user=other_user, content="Other's post")
        url = reverse("posts:post-detail", kwargs={"pk": other_post.id})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Post.objects.filter(pk=other_post.id).exists()


@pytest.mark.django_db
class TestPostLike:
    """Tests for post like endpoint."""
    
    def test_like_post(self, authenticated_client, post, user):
        """Test liking a post."""
        url = reverse("posts:post-like", kwargs={"pk": post.id})
        
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["liked"] is True
        assert response.data["likes_count"] == 1
    
    def test_unlike_post(self, authenticated_client, post, user):
        """Test unliking a post (toggle)."""
        url = reverse("posts:post-like", kwargs={"pk": post.id})
        
        # First like
        authenticated_client.post(url)
        
        # Then unlike
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["liked"] is False
        assert response.data["likes_count"] == 0
    
    def test_like_post_unauthenticated(self, api_client, post):
        """Test liking without authentication."""
        url = reverse("posts:post-like", kwargs={"pk": post.id})
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestFollowingFeed:
    """Tests for following feed endpoint."""
    
    def test_following_feed(self, authenticated_client, user, other_user):
        """Test getting posts from followed users."""
        from apps.follows.models import Follow
        
        # Create follow relationship
        Follow.objects.create(follower=user, following=other_user)
        
        # Create posts
        Post.objects.create(user=other_user, content="Post from followed user")
        
        url = reverse("posts:post-following")
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["content"] == "Post from followed user"
    
    def test_following_feed_unauthenticated(self, api_client):
        """Test following feed without authentication."""
        url = reverse("posts:post-following")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

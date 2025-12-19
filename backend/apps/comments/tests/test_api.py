"""Tests for Comment API endpoints."""
import pytest
from django.urls import reverse
from rest_framework import status

from apps.comments.models import Comment


@pytest.mark.django_db
class TestCommentList:
    """Tests for comment list endpoint."""
    
    def test_list_comments(self, api_client, comment):
        """Test listing comments for a post."""
        url = reverse("comments:comment-list", kwargs={"post_id": comment.post.id})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["content"] == comment.content
    
    def test_list_comments_empty(self, api_client, post):
        """Test listing comments when none exist."""
        url = reverse("comments:comment-list", kwargs={"post_id": post.id})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []


@pytest.mark.django_db
class TestCommentCreate:
    """Tests for comment creation endpoint."""
    
    def test_create_comment(self, authenticated_client, post, user):
        """Test creating a comment."""
        url = reverse("comments:comment-list", kwargs={"post_id": post.id})
        data = {"content": "Great post!"}
        
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["content"] == "Great post!"
        assert Comment.objects.filter(post=post, user=user).exists()
        
        # Verify post comment count updated
        post.refresh_from_db()
        assert post.comments_count == 1
    
    def test_create_comment_unauthenticated(self, api_client, post):
        """Test creating comment without authentication."""
        url = reverse("comments:comment-list", kwargs={"post_id": post.id})
        data = {"content": "Anonymous comment"}
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_comment_empty_content(self, authenticated_client, post):
        """Test creating comment with empty content."""
        url = reverse("comments:comment-list", kwargs={"post_id": post.id})
        data = {"content": ""}
        
        response = authenticated_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCommentDelete:
    """Tests for comment deletion endpoint."""
    
    def test_delete_own_comment(self, authenticated_client, comment, user):
        """Test deleting own comment."""
        post = comment.post
        url = reverse("comments:comment-delete", kwargs={"pk": comment.id})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(pk=comment.id).exists()
        
        # Verify post comment count updated
        post.refresh_from_db()
        assert post.comments_count == 0
    
    def test_delete_other_user_comment(self, authenticated_client, post, other_user):
        """Test that users cannot delete others' comments."""
        other_comment = Comment.objects.create(
            user=other_user,
            post=post,
            content="Other's comment",
        )
        url = reverse("comments:comment-delete", kwargs={"pk": other_comment.id})
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Comment.objects.filter(pk=other_comment.id).exists()

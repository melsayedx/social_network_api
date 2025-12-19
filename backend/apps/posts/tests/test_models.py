"""Tests for Post model."""
import pytest
from uuid import UUID

from apps.posts.models import Post


@pytest.mark.django_db
class TestPostModel:
    """Tests for Post model."""
    
    def test_post_has_uuid7_id(self, post):
        """Test that post ID is a valid UUIDv7."""
        assert isinstance(post.id, UUID)
        assert post.id.version == 7
    
    def test_post_metadata_default(self, user):
        """Test that metadata defaults to empty dict."""
        post = Post.objects.create(user=user, content="Test")
        assert post.metadata == {}
    
    def test_post_metadata_hashtags(self, user):
        """Test storing hashtags in metadata."""
        post = Post.objects.create(
            user=user,
            content="Testing Django",
            metadata={"hashtags": ["django", "python"]},
        )
        
        post.refresh_from_db()
        assert post.hashtags == ["django", "python"]
    
    def test_post_is_edited(self, user):
        """Test is_edited property."""
        post = Post.objects.create(user=user, content="Original")
        assert post.is_edited is False
        
        post.metadata = {"edited": True}
        post.save()
        assert post.is_edited is True
    
    def test_post_str(self, post):
        """Test post string representation."""
        assert post.user.username in str(post)
    
    def test_post_likes_count_default(self, user):
        """Test likes_count defaults to 0."""
        post = Post.objects.create(user=user, content="Test")
        assert post.likes_count == 0
    
    def test_post_comments_count_default(self, user):
        """Test comments_count defaults to 0."""
        post = Post.objects.create(user=user, content="Test")
        assert post.comments_count == 0
    
    def test_post_ordering(self, user):
        """Test posts are ordered by created_at descending."""
        post1 = Post.objects.create(user=user, content="First")
        post2 = Post.objects.create(user=user, content="Second")
        
        posts = list(Post.objects.all())
        assert posts[0] == post2  # Newest first
        assert posts[1] == post1

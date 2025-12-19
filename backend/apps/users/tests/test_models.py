"""Tests for User model."""
import pytest
from uuid import UUID

from apps.users.models import User


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""
    
    def test_user_has_uuid7_id(self, user):
        """Test that user ID is a valid UUID."""
        assert isinstance(user.id, UUID)
        # UUIDv7 has version 7
        assert user.id.version == 7
    
    def test_user_preferences_default(self, db):
        """Test that preferences default to empty dict."""
        user = User.objects.create_user(
            username="preftest",
            email="pref@example.com",
            password="testpass123",
        )
        assert user.preferences == {}
    
    def test_user_preferences_update(self, user):
        """Test updating user preferences."""
        user.preferences = {
            "theme": "dark",
            "notifications": {"email": True, "push": False},
        }
        user.save()
        
        user.refresh_from_db()
        assert user.preferences["theme"] == "dark"
        assert user.preferences["notifications"]["email"] is True
    
    def test_user_bio_default(self, db):
        """Test that bio defaults to empty string."""
        user = User.objects.create_user(
            username="biotest",
            email="bio@example.com",
            password="testpass123",
        )
        assert user.bio == ""
    
    def test_user_str(self, user):
        """Test user string representation."""
        assert str(user) == user.username
    
    def test_followers_count(self, user, other_user):
        """Test followers_count property."""
        from apps.follows.models import Follow
        
        assert user.followers_count == 0
        
        Follow.objects.create(follower=other_user, following=user)
        assert user.followers_count == 1
    
    def test_following_count(self, user, other_user):
        """Test following_count property."""
        from apps.follows.models import Follow
        
        assert user.following_count == 0
        
        Follow.objects.create(follower=user, following=other_user)
        assert user.following_count == 1
    
    def test_posts_count(self, user):
        """Test posts_count property."""
        from apps.posts.models import Post
        
        assert user.posts_count == 0
        
        Post.objects.create(user=user, content="Test post")
        assert user.posts_count == 1

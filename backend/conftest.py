"""Pytest configuration and fixtures."""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Return an API client for testing."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    from apps.users.models import User
    
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def other_user(db):
    """Create and return another test user."""
    from apps.users.models import User
    
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="testpass123",
    )


@pytest.fixture
def authenticated_client(api_client, user) -> APIClient:
    """Return an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def post(db, user):
    """Create and return a test post."""
    from apps.posts.models import Post
    
    return Post.objects.create(
        user=user,
        content="This is a test post.",
        metadata={"hashtags": ["test", "example"]},
    )


@pytest.fixture
def comment(db, user, post):
    """Create and return a test comment."""
    from apps.comments.models import Comment
    
    return Comment.objects.create(
        user=user,
        post=post,
        content="This is a test comment.",
    )

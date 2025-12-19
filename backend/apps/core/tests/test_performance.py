"""Performance tests for query optimization."""
import pytest
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext

from apps.posts.models import Post
from apps.users.models import User


@pytest.mark.django_db
class TestQueryOptimization:
    """Tests to verify N+1 query elimination."""
    
    def test_post_list_query_count(self, api_client, user):
        """Test that post list uses constant number of queries regardless of posts count."""
        # Create 20 posts
        for i in range(20):
            Post.objects.create(user=user, content=f"Post {i}")
        
        # Reset query log
        reset_queries()
        
        with CaptureQueriesContext(connection) as context:
            from django.urls import reverse
            url = reverse("posts:post-list")
            response = api_client.get(url)
            
            assert response.status_code == 200
        
        # Should be constant queries (not N+1)
        # Expected: 1 for posts + 1 for count = ~2-4 queries
        assert len(context.captured_queries) <= 5, (
            f"Too many queries: {len(context.captured_queries)} queries. "
            f"Possible N+1 issue."
        )
    
    def test_post_list_with_user_no_n_plus_1(self, api_client, user, other_user):
        """Test that user data doesn't cause N+1 queries."""
        # Create posts by different users
        for i in range(5):
            Post.objects.create(user=user, content=f"User post {i}")
            Post.objects.create(user=other_user, content=f"Other post {i}")
        
        reset_queries()
        
        with CaptureQueriesContext(connection) as context:
            from django.urls import reverse
            url = reverse("posts:post-list")
            response = api_client.get(url)
            
            assert response.status_code == 200
            assert len(response.data["results"]) == 10
        
        # Queries should still be constant despite multiple users
        assert len(context.captured_queries) <= 5
    
    def test_authenticated_user_like_annotation(self, authenticated_client, user, post):
        """Test that is_liked annotation doesn't cause extra queries."""
        reset_queries()
        
        with CaptureQueriesContext(connection) as context:
            from django.urls import reverse
            url = reverse("posts:post-list")
            response = authenticated_client.get(url)
            
            assert response.status_code == 200
        
        # With like annotation, should still be efficient
        assert len(context.captured_queries) <= 6


@pytest.mark.django_db
class TestCaching:
    """Tests for caching functionality."""
    
    def test_cache_manager_user(self):
        """Test user caching."""
        from apps.core.cache import CacheManager
        
        user_id = "test-user-123"
        user_data = {"username": "testuser", "bio": "Test bio"}
        
        # Cache should be empty initially
        assert CacheManager.get_cached_user(user_id) is None
        
        # Cache the user
        CacheManager.cache_user(user_id, user_data)
        
        # Should retrieve cached data
        cached = CacheManager.get_cached_user(user_id)
        assert cached == user_data
        
        # Invalidate cache
        CacheManager.invalidate_user(user_id)
        
        # Should be empty again
        assert CacheManager.get_cached_user(user_id) is None
    
    def test_cache_manager_feed(self):
        """Test feed caching."""
        from apps.core.cache import CacheManager
        
        user_id = "test-user-456"
        feed_data = [{"id": "1", "content": "Post 1"}, {"id": "2", "content": "Post 2"}]
        
        # Cache should be empty
        assert CacheManager.get_cached_feed(user_id) is None
        
        # Cache the feed
        CacheManager.cache_feed(user_id, feed_data)
        
        # Should retrieve cached data
        cached = CacheManager.get_cached_feed(user_id)
        assert cached == feed_data
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        from apps.core.cache import cache_key
        
        key = cache_key("prefix", "arg1", "arg2")
        assert key == "prefix:arg1:arg2"
        
        # With numbers
        key = cache_key("user", 123, "profile")
        assert key == "user:123:profile"

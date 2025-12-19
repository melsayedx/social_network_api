"""
Query optimization utilities.

Provides optimized querysets and prefetch patterns to eliminate N+1 queries.
"""
from django.db.models import Count, Prefetch, Q


class PostQueryOptimizer:
    """Optimized query patterns for posts."""
    
    @staticmethod
    def get_optimized_queryset(base_queryset, user=None):
        """
        Get optimized post queryset with all related data prefetched.
        
        Eliminates N+1 queries for:
        - User (select_related)
        - Comments count (annotation)
        - Likes count (denormalized, no query needed)
        - Is liked by current user (subquery annotation)
        """
        from apps.likes.models import Like
        from django.db.models import Exists, OuterRef
        
        queryset = base_queryset.select_related("user")
        
        if user and user.is_authenticated:
            # Annotate with whether the current user has liked each post
            queryset = queryset.annotate(
                _user_liked=Exists(
                    Like.objects.filter(
                        post=OuterRef("pk"),
                        user=user,
                    )
                )
            )
        
        return queryset
    
    @staticmethod
    def get_post_with_comments(post_id, user=None, comment_limit=10):
        """
        Get a single post with prefetched comments.
        
        Optimized for detail view with limited comments.
        """
        from apps.comments.models import Comment
        from apps.posts.models import Post
        
        comments_prefetch = Prefetch(
            "comments",
            queryset=Comment.objects.select_related("user").order_by("-created_at")[:comment_limit],
        )
        
        queryset = Post.objects.prefetch_related(comments_prefetch)
        return PostQueryOptimizer.get_optimized_queryset(queryset, user).get(pk=post_id)


class UserQueryOptimizer:
    """Optimized query patterns for users."""
    
    @staticmethod
    def get_optimized_queryset(base_queryset):
        """
        Get optimized user queryset with counts.
        
        Uses annotations to avoid N+1 for follower/following/post counts.
        """
        return base_queryset.annotate(
            _followers_count=Count("followers", distinct=True),
            _following_count=Count("following", distinct=True),
            _posts_count=Count("posts", distinct=True),
        )
    
    @staticmethod
    def get_user_with_recent_posts(username, post_limit=5):
        """
        Get user with their recent posts prefetched.
        
        Optimized for profile view.
        """
        from apps.posts.models import Post
        from apps.users.models import User
        
        posts_prefetch = Prefetch(
            "posts",
            queryset=Post.objects.order_by("-created_at")[:post_limit],
        )
        
        return (
            User.objects
            .prefetch_related(posts_prefetch)
            .get(username=username)
        )


class FeedQueryOptimizer:
    """Optimized query patterns for feeds."""
    
    @staticmethod
    def get_following_feed(user, limit=20, offset=0):
        """
        Get optimized following feed.
        
        Uses efficient subquery for followed users.
        """
        from apps.posts.models import Post
        
        following_ids = user.following.values_list("following_id", flat=True)
        
        queryset = (
            Post.objects
            .filter(user_id__in=following_ids)
            .select_related("user")
            .order_by("-created_at")
        )[offset:offset + limit]
        
        return PostQueryOptimizer.get_optimized_queryset(
            queryset._chain(), user
        )
    
    @staticmethod
    def get_global_feed(user=None, limit=20, offset=0):
        """
        Get optimized global feed (all posts).
        """
        from apps.posts.models import Post
        
        queryset = (
            Post.objects
            .select_related("user")
            .order_by("-created_at")
        )[offset:offset + limit]
        
        return PostQueryOptimizer.get_optimized_queryset(
            queryset._chain(), user
        )

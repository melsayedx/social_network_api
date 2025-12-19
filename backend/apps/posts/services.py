"""Post services - business logic layer."""
from django.db import transaction
from django.db.models import F

from apps.likes.models import Like

from .models import Post


class PostService:
    """Service class for post-related business logic."""
    
    @staticmethod
    def create_post(user, content: str, hashtags: list[str] | None = None) -> Post:
        """
        Create a new post with optional hashtags.
        
        Args:
            user: The user creating the post
            content: Post content
            hashtags: Optional list of hashtags
            
        Returns:
            The created Post instance
        """
        metadata = {}
        if hashtags:
            metadata["hashtags"] = [h.lower().strip("#") for h in hashtags]
        
        return Post.objects.create(
            user=user,
            content=content.strip(),
            metadata=metadata,
        )
    
    @staticmethod
    def update_post(post: Post, content: str) -> Post:
        """
        Update a post and track edit history.
        
        Args:
            post: The post to update
            content: New content
            
        Returns:
            The updated Post instance
        """
        if content != post.content:
            metadata = post.metadata or {}
            metadata["edited"] = True
            
            # Track edit history (keep last 5)
            edit_history = metadata.get("edit_history", [])
            edit_history.append({
                "content": post.content,
                "edited_at": post.updated_at.isoformat() if post.updated_at else None,
            })
            metadata["edit_history"] = edit_history[-5:]
            
            post.content = content.strip()
            post.metadata = metadata
            post.save(update_fields=["content", "metadata", "updated_at"])
        
        return post
    
    @staticmethod
    @transaction.atomic
    def toggle_like(user, post: Post) -> tuple[bool, int]:
        """
        Toggle like on a post.
        
        Args:
            user: The user toggling the like
            post: The post to like/unlike
            
        Returns:
            Tuple of (is_liked, new_likes_count)
        """
        like, created = Like.objects.get_or_create(user=user, post=post)
        
        if created:
            Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") + 1)
            post.refresh_from_db()
            return True, post.likes_count
        else:
            like.delete()
            Post.objects.filter(pk=post.pk).update(likes_count=F("likes_count") - 1)
            post.refresh_from_db()
            return False, post.likes_count
    
    @staticmethod
    def get_following_feed(user, limit: int = 20):
        """
        Get posts from users that the given user follows.
        
        Args:
            user: The user requesting the feed
            limit: Maximum number of posts to return
            
        Returns:
            QuerySet of posts
        """
        following_ids = user.following.values_list("following_id", flat=True)
        return (
            Post.objects
            .filter(user_id__in=following_ids)
            .select_related("user")
            .order_by("-created_at")[:limit]
        )
    
    @staticmethod
    def get_user_liked_post_ids(user) -> set:
        """
        Get set of post IDs that a user has liked.
        
        Args:
            user: The user
            
        Returns:
            Set of post UUIDs
        """
        return set(Like.objects.filter(user=user).values_list("post_id", flat=True))

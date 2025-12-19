"""Follow services - business logic layer."""
from django.db import IntegrityError

from apps.users.models import User

from .models import Follow


class FollowService:
    """Service class for follow-related business logic."""
    
    @staticmethod
    def toggle_follow(follower: User, following: User) -> tuple[bool, int]:
        """
        Toggle follow status between two users.
        
        Args:
            follower: The user who wants to follow/unfollow
            following: The user to be followed/unfollowed
            
        Returns:
            Tuple of (is_following, followers_count)
            
        Raises:
            ValueError: If trying to follow self
        """
        if follower.id == following.id:
            raise ValueError("Cannot follow yourself")
        
        try:
            # Try to create follow
            Follow.objects.create(follower=follower, following=following)
            return True, following.followers_count
        except IntegrityError:
            # Already following, so unfollow
            Follow.objects.filter(follower=follower, following=following).delete()
            return False, following.followers_count
    
    @staticmethod
    def is_following(follower: User, following: User) -> bool:
        """
        Check if one user is following another.
        
        Args:
            follower: The potential follower
            following: The user potentially being followed
            
        Returns:
            True if follower is following following
        """
        return Follow.objects.filter(follower=follower, following=following).exists()
    
    @staticmethod
    def get_followers(user: User):
        """
        Get all followers of a user.
        
        Args:
            user: The user whose followers to get
            
        Returns:
            QuerySet of Follow objects
        """
        return Follow.objects.filter(following=user).select_related("follower")
    
    @staticmethod
    def get_following(user: User):
        """
        Get all users that a user is following.
        
        Args:
            user: The user
            
        Returns:
            QuerySet of Follow objects
        """
        return Follow.objects.filter(follower=user).select_related("following")
    
    @staticmethod
    def get_mutual_followers(user1: User, user2: User):
        """
        Get users who follow both user1 and user2.
        
        Args:
            user1: First user
            user2: Second user
            
        Returns:
            QuerySet of User objects
        """
        followers1 = set(Follow.objects.filter(following=user1).values_list("follower_id", flat=True))
        followers2 = set(Follow.objects.filter(following=user2).values_list("follower_id", flat=True))
        mutual_ids = followers1 & followers2
        return User.objects.filter(id__in=mutual_ids)

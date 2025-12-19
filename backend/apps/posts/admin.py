"""Post admin configuration."""
from django.contrib import admin

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model."""
    
    list_display = ["id", "user", "content_preview", "likes_count", "comments_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "user__username"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "likes_count", "comments_count", "created_at", "updated_at"]
    
    def content_preview(self, obj: Post) -> str:
        """Show first 50 characters of content."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content"

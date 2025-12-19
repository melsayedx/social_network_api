"""Comment admin configuration."""
from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin configuration for Comment model."""
    
    list_display = ["id", "user", "post", "content_preview", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["content", "user__username"]
    ordering = ["-created_at"]
    
    def content_preview(self, obj: Comment) -> str:
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content"

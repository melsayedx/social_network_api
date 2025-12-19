"""Like admin configuration."""
from django.contrib import admin

from .models import Like


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin configuration for Like model."""
    
    list_display = ["id", "user", "post", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username"]
    ordering = ["-created_at"]

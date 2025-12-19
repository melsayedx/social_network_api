"""User admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    
    list_display = ["username", "email", "is_staff", "is_active", "created_at"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email"]
    ordering = ["-created_at"]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("bio", "avatar", "preferences")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Profile", {"fields": ("email", "bio")}),
    )

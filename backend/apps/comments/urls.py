"""Comment URL patterns."""
from django.urls import path

from .views import CommentViewSet

app_name = "comments"

urlpatterns = [
    # Nested under posts
    path(
        "posts/<uuid:post_id>/comments/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="comment-list",
    ),
    # Direct access for delete
    path(
        "comments/<uuid:pk>/",
        CommentViewSet.as_view({"delete": "destroy"}),
        name="comment-delete",
    ),
]

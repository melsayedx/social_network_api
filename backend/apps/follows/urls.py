"""Follow URL patterns."""
from django.urls import path

from .views import FollowViewSet

app_name = "follows"

urlpatterns = [
    path(
        "users/<str:username>/follow/",
        FollowViewSet.as_view({"post": "toggle"}),
        name="follow-toggle",
    ),
    path(
        "users/<str:username>/followers/",
        FollowViewSet.as_view({"get": "followers"}),
        name="followers-list",
    ),
    path(
        "users/<str:username>/following/",
        FollowViewSet.as_view({"get": "following"}),
        name="following-list",
    ),
]

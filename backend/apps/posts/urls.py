"""Post URL patterns using Router."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet

app_name = "posts"

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
]

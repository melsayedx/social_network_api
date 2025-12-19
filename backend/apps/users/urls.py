"""User URL patterns using Routers for GenericViewSets."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import AuthViewSet, UserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Authentication - JWT tokens
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # Authentication - Registration (using ViewSet action)
    path("auth/register/", AuthViewSet.as_view({"post": "register"}), name="register"),
    
    # Users - via router
    path("", include(router.urls)),
]

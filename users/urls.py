from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.UserViews import UserViewSet


# Create a router and register the UserViewSet
router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

# Include the router URLs in urlpatterns
urlpatterns = [
    path("", include(router.urls)),
]

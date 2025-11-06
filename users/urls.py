from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views.UserViews import UserViewSet
from .views.RegisterViews import RegisterView

from . import views



router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

# Include the router URLs in urlpatterns
urlpatterns = [
    path("", include(router.urls)),
    path('register', RegisterView.as_view(), name='register'),
]

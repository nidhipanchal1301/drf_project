from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    hello_world,
    PostDetailAPIView,
    PostListCreateMixins,
    PostViewSet,
    CommentViewSet,
    TagViewSet,
    PostListAPIView,
    PostCreateAPIView,
    PostRetrieveAPIView,
    PostUpdateAPIView,
    PostDeleteAPIView,
    AnalyticsAPIView,
    CachedPostListAPIView,
)

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("hello/", hello_world, name="hello"),
    path("posts-mixins/", PostListCreateMixins.as_view(), name="posts-mixins"),
    path("posts/<int:pk>/detail/", PostDetailAPIView.as_view(), name="post-detail-apiview"),
    path("cached-posts/", CachedPostListAPIView.as_view(), name="cached-posts"),
    path('analytics/', AnalyticsAPIView.as_view(), name='analytics'),
    
    # CRUD endpoints for generic apiview
    path("posts/", PostListAPIView.as_view(), name="post-list"),
    path("posts/create/", PostCreateAPIView.as_view(), name="post-create"),
    path("posts/<int:pk>/", PostRetrieveAPIView.as_view(), name="post-detail"),
    path("posts/<int:pk>/update/", PostUpdateAPIView.as_view(), name="post-update"),
    path("posts/<int:pk>/delete/", PostDeleteAPIView.as_view(), name="post-delete"),
    path("", include(router.urls)),
]

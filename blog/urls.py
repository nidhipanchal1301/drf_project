from rest_framework.routers import DefaultRouter

from django.urls import path, include

from .views import (api_status, PostDetailAPIView, PostListCreateMixins, PostViewSet, CommentViewSet, TagViewSet, PostListAPIView,
                    PostCreateAPIView, PostRetrieveAPIView, PostUpdateAPIView, PostDeleteAPIView, AnalyticsAPIView, CachedPostListAPIView, )


router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="post")
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    path("status/", api_status, name="api-status"),
    path("mixins/", PostListCreateMixins.as_view(), name="posts-mixins"),
    path("<int:pk>/detail/", PostDetailAPIView.as_view(), name="post-detail-apiview"),
    path("cached-posts/", CachedPostListAPIView.as_view(), name="cached-posts"),
    path("analytics/", AnalyticsAPIView.as_view(), name="analytics"),

    # CRUD endpoints for generic APIViews
    path("list/", PostListAPIView.as_view(), name="post-list"),
    path("create/", PostCreateAPIView.as_view(), name="post-create"),
    path("<int:pk>/", PostRetrieveAPIView.as_view(), name="post-detail"),
    path("<int:pk>/update/", PostUpdateAPIView.as_view(), name="post-update"),
    path("<int:pk>/delete/", PostDeleteAPIView.as_view(), name="post-delete"),

    # Router URLs
    path("", include(router.urls)),
]

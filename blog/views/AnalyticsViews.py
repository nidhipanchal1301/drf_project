from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg
from ..models import Post, Comment

class AnalyticsAPIView(APIView):  # Rename here
    def get(self, request):
        posts_per_author = Post.objects.values("author__username").annotate(
            total_posts=Count("id"),
            post_titles=ArrayAgg("title", distinct=True)
        ).order_by("author__username")

        comments_per_post = Comment.objects.values("post__title").annotate(
            total_comments=Count("id"),
            comment_texts=ArrayAgg("content", distinct=True)
        ).order_by("post__title")

        posts_per_tag = Post.objects.values("tags__name").annotate(
            total_posts=Count("id"),
            post_titles=ArrayAgg("title", distinct=True)
        ).order_by("tags__name")

        return Response({
            "posts_per_author": list(posts_per_author),
            "comments_per_post": list(comments_per_post),
            "posts_per_tag": list(posts_per_tag),
        })

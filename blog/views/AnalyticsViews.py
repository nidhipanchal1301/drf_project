from rest_framework.views import APIView
from rest_framework.response import Response

from django.db.models import Count,  OuterRef, Subquery, Exists, Case, When, Value, BooleanField
from django.contrib.postgres.aggregates import ArrayAgg

from ..models import Post, Comment, Tag

from django.contrib.auth import get_user_model


User = get_user_model()

class AnalyticsAPIView(APIView): 

    def get(self, request):
        posts_per_author = (
            User.objects.annotate(
                total_posts=Count('post', distinct=True),
                post_titles=ArrayAgg('post__title', distinct=True)
            )
            .values('username', 'total_posts', 'post_titles')
            .order_by('username')
        )

        latest_comment_subquery = Comment.objects.filter(post=OuterRef('pk')).order_by('created_at').values('content')[:1]

        comments_per_post = (
            Post.objects.select_related('author')  
                .prefetch_related('comments')   
                .annotate(
                    total_comments=Count('comments', distinct=True),
                    comment_texts=ArrayAgg('comments__content', distinct=True),
                    latest_comment=Subquery(latest_comment_subquery),
                    has_comments=Exists(Comment.objects.filter(post=OuterRef('pk'))),
                )
                .values('title', 'total_comments', 'comment_texts', 'latest_comment', 'has_comments')
                .order_by('title')
        )

        posts_per_tag = (
            Tag.objects.prefetch_related('posts')  
                .annotate(
                    total_posts=Count('posts', distinct=True),
                    post_titles=ArrayAgg('posts__title', distinct=True),
            )
            .values('name', 'total_posts', 'post_titles')
            .order_by('name')
        )


        return Response({
            "posts_per_author": list(posts_per_author),
            "comments_per_post": list(comments_per_post),
            "posts_per_tag": list(posts_per_tag),
        })

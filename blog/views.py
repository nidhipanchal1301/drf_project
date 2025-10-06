from rest_framework import viewsets, generics, mixins, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated,  AllowAny
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.db.models import Count
from django.contrib.postgres.aggregates import ArrayAgg
from .models import Post, Comment, Tag
from .serializers import BasicPostSerializer, PostSerializer, CommentSerializer, TagSerializer
from .permissions import IsOwnerOrReadOnly
from .throttling import TenPerHourUserThrottle
from .pagination import StandardResultsSetPagination
        
from django.db.models import (
    Count, Sum, OuterRef, Subquery, Exists,
    Case, When, Value, BooleanField, ExpressionWrapper, F, DurationField, IntegerField,
)
from django.db.models.functions import Length
from django.contrib.postgres.aggregates import ArrayAgg
from django.utils.timezone import now


# Function Based View 
@api_view(["GET"])
def hello_world(request):
    return Response({"message": "Hello from DRF function-based view!"})


# class-based apiview
@method_decorator(csrf_exempt, name='dispatch')
class PostDetailAPIView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(post, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data, context={"request": request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


# Mixins + GenericAPIView 
class PostListCreateMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = (
        Post.objects.select_related("author")
        .prefetch_related("tags", "comments")
        .only("id", "title", "author", "created_at") 
    )
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        return self.create(request, *args, **kwargs)
    

# Optimized Post List with annotations
@method_decorator(cache_page(60), name='dispatch')
class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["author__username", "tags__name"]
    search_fields = ["title", "content", "author__username"]
    ordering_fields = ["created_at", "title"]
    pagination_class = StandardResultsSetPagination
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        latest_comment_subquery = Comment.objects.filter(
            post=OuterRef("pk")
        ).order_by("-created_at").values("content")[:1]

        return (
            Post.objects.select_related("author")
            .prefetch_related("tags", "comments")
            .only("id", "title", "author", "created_at", "image")
            .defer("content")
            .annotate(
                comment_count=Count("comments"),
                tag_names=ArrayAgg("tags__name", distinct=True),
                latest_comment=Subquery(latest_comment_subquery),
                has_comments=Exists(Comment.objects.filter(post=OuterRef("pk"))),
                has_image=Case(
                    When(image__isnull=False, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                title_length=Length("title"),
                doubled_title_len=ExpressionWrapper(
                    F("title_length") * 2, output_field=IntegerField()
                ),
            )
            .order_by("-created_at")
        )


@method_decorator(cache_page(60), name='dispatch')
class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]



class PostRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class PostUpdateAPIView(generics.UpdateAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class PostDeleteAPIView(generics.DestroyAPIView):
    queryset = Post.objects.all().only("id")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]



# ViewSet + Router (recommended) 
@method_decorator(csrf_exempt, name="dispatch")
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").defer("content", "image").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    throttle_classes = [TenPerHourUserThrottle]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["author__username", "tags__name"]
    search_fields = ["title", "content", "author__username"]
    ordering_fields = ["created_at", "title"]

    
    @method_decorator(csrf_exempt)
    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        post = self.get_object()
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        post.image = file_obj
        post.save()
        return Response(PostSerializer(post, context={"request": request}).data)
    


# Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("post").all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)





# Tag View (read-only) 
class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().only("id", "name")
    serializer_class = TagSerializer
    permission_classes = [ AllowAny]


# Cached Post List
@method_decorator(cache_page(60), name='dispatch')  
class CachedPostListAPIView(generics.ListAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags").all()
    serializer_class = PostSerializer



class AnalyticsAPIView(APIView):
    def get(self, request):
        # Posts per author
        posts_per_author = Post.objects.values("author__username").annotate(
            total_posts=Count("id"),
            post_titles=ArrayAgg("title", distinct=True)
        ).order_by("author__username")

        # For Comments 
        comments_per_post = Comment.objects.values("post__title").annotate(
            total_comments=Count("id"),
            comment_texts=ArrayAgg("content", distinct=True)
        ).order_by("post__title")

        # For Posts
        posts_per_tag = Post.objects.values("tags__name").annotate(
            total_posts=Count("id"),
            post_titles=ArrayAgg("title", distinct=True)
        ).order_by("tags__name")

        return Response({
            "posts_per_author": list(posts_per_author),
            "comments_per_post": list(comments_per_post),
            "posts_per_tag": list(posts_per_tag),
        })
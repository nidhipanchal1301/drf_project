from rest_framework import generics, viewsets, mixins, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from django.shortcuts import get_object_or_404

from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page

from django.db.models import Count, OuterRef, Subquery, Exists, Case, When, Value, BooleanField, F, IntegerField, ExpressionWrapper
from django.db.models.functions import Length

from django.contrib.postgres.aggregates import ArrayAgg

from ..models import Post, Comment

from ..serializers import PostSerializer

from ..permissions import IsOwnerOrReadOnly

from ..pagination import StandardResultsSetPagination

from ..throttling import TenPerHourUserThrottle

from django_filters.rest_framework import DjangoFilterBackend

from ..filters import PostFilter



@method_decorator(csrf_exempt, name='dispatch')
class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


class PostListCreateMixins(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").only("id", "title", "author", "created_at")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@method_decorator(cache_page(60), name='dispatch')
class PostListAPIView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["author__username", "tags__name"]
    search_fields = ["title", "content", "author__username"]
    ordering_fields = ["created_at", "title"]
    pagination_class = StandardResultsSetPagination
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        latest_comment_subquery = Comment.objects.filter(post=OuterRef("pk")).order_by("-created_at").values("content")[:1]
        return (
            Post.objects.select_related("author")
            .prefetch_related("tags", "comments__author")
            # .only("id", "title", "author", "created_at", "image")
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
                doubled_title_len=ExpressionWrapper(F("title_length") * 2, output_field=IntegerField()),
            )
            .order_by("-created_at")
        )


@method_decorator(cache_page(60), name='dispatch')
class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostUpdateAPIView(generics.UpdateAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


class PostDeleteAPIView(generics.DestroyAPIView):
    queryset = Post.objects.all().only("id")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


@method_decorator(csrf_exempt, name="dispatch")
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments__author",).defer("content", "image").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    throttle_classes = [TenPerHourUserThrottle]
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["author__username", "tags__name"]
    filterset_class = PostFilter
    filter_backends = [DjangoFilterBackend]
    search_fields = ["title", "content", "author__username"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        queryset = super().get_queryset()


        queryset = (
            queryset
            .filter(author__is_active=True)
            .select_related("author")
            .prefetch_related("tags", "comments__author")
            .defer("content", "image")
            .order_by("-created_at")
        )
    
        limit = self.request.query_params.get("limit")
        if limit:
            try:
                limit = int(limit)
                queryset = queryset[:limit]
            except ValueError:
                pass  
        return queryset

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        post = self.get_object()
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        post.image = file_obj
        post.save()
        return Response(PostSerializer(post, context={"request": request}).data)


    @action(detail=True, methods=["get"])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = (
            Comment.objects.filter(post=post, parent__isnull=True)
            .select_related("author")
            .prefetch_related(Prefetch("replies", queryset=Comment.objects.select_related("author")))
            .order_by("created_at")
        )
        serializer = CommentSerializer(comments, many=True, context={"request": request})
        return Response(serializer.data)


@method_decorator(cache_page(60), name='dispatch')
class CachedPostListAPIView(generics.ListAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags").all()
    serializer_class = PostSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

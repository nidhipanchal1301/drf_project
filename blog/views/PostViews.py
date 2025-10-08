from rest_framework import generics, viewsets, mixins, status
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


# -------------------- POST DETAIL --------------------
@method_decorator(csrf_exempt, name='dispatch')
class PostDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrReadOnly]
    parser_classes = [JSONParser, FormParser, MultiPartParser]


# -------------------- LIST & CREATE --------------------
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


# -------------------- LIST API WITH ANNOTATIONS --------------------
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
        latest_comment_subquery = Comment.objects.filter(post=OuterRef("pk")).order_by("-created_at").values("content")[:1]
        return (
            Post.objects.select_related("author")
            .prefetch_related("tags", "comments")
            .only("id", "title", "author", "created_at", "image")
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


# -------------------- CREATE API --------------------
@method_decorator(cache_page(60), name='dispatch')
class PostCreateAPIView(generics.CreateAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# -------------------- RETRIEVE API --------------------
class PostRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# -------------------- UPDATE API --------------------
class PostUpdateAPIView(generics.UpdateAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags", "comments").all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)


# -------------------- DELETE API --------------------
class PostDeleteAPIView(generics.DestroyAPIView):
    queryset = Post.objects.all().only("id")
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# -------------------- VIEWSET --------------------
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

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        post = self.get_object()
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        post.image = file_obj
        post.save()
        return Response(PostSerializer(post, context={"request": request}).data)


# -------------------- CACHED LIST API --------------------
@method_decorator(cache_page(60), name='dispatch')
class CachedPostListAPIView(generics.ListAPIView):
    queryset = Post.objects.select_related("author").prefetch_related("tags").all()
    serializer_class = PostSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

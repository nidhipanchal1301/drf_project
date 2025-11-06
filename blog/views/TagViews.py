from rest_framework import viewsets, status

from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.decorators import action

from rest_framework.response import Response

from ..models import Tag, Post, Comment

from ..serializers import TagSerializer, CommentSerializer

from django.db.models import Prefetch



class TagViewSet(viewsets.ModelViewSet):
    queryset = (
        Tag.objects.all()
        .only("id", "name")
        .prefetch_related(
            Prefetch(
                "posts",
                queryset=Post.objects.only("id", "title").prefetch_related(
                    Prefetch(
                        "comments",
                        queryset=Comment.objects.select_related("author").only(
                            "id", "content", "author_id", "created_at").distinct()
                    )
                )
            )
        )
    )
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        tag = self.get_object()
        post_id = request.data.get("post_id")
        content = request.data.get("content")

        if not post_id or not content:
            return Response({"detail": "Post ID and content are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            post = Post.objects.get(id=post_id, tags=tag)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found for this tag"}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )

        serializer = CommentSerializer(comment, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
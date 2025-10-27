from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from ..models import Comment, Post
from ..serializers import CommentSerializer
from ..permissions import IsOwnerOrReadOnly


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("post").all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user, post=post)

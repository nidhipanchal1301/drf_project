from rest_framework import serializers
from ..models import Tag, Comment, Post


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "post", "parent", "created_at")
        read_only_fields = ("author", "created_at")


class TagSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ("id", "name", "comments")
  
    def get_comments(self, tag):
        comments = Comment.objects.filter(post__tags=tag)
        return CommentSerializer(comments, many=True, context=self.context).data

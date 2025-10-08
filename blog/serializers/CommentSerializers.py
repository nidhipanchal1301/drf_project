from rest_framework import serializers
from ..models import Comment

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveField(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "parent", "replies", "created_at")

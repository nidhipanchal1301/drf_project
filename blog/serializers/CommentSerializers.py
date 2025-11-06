from rest_framework import serializers

from ..models import Comment

from django.contrib.auth import get_user_model

User = get_user_model()



class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class CommentChildSerializer(serializers.ModelSerializer):
    author = UserDisplaySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at")
        

class CommentSerializer(serializers.ModelSerializer):
    author = UserDisplaySerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "content", "created_at")
        read_only_fields = ()
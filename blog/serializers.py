from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Tag

# Basic Serializer
class BasicPostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    def create(self, validated_data):
        return {"title": validated_data["title"], "content": validated_data["content"]}


# ModelSerializers & nested 
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

# Nested comment
class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    replies = RecursiveField(many=True, read_only=True)
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "parent", "replies", "created_at"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  
    comments = CommentSerializer(many=True, read_only=True)  
    tags = TagSerializer(many=True, read_only=True)          
    tag_ids = serializers.PrimaryKeyRelatedField(           
        queryset=Tag.objects.all(),
        many=True,
        source="tags"
    )

    #analytics fields
    comment_count = serializers.IntegerField(read_only=True)
    has_image = serializers.BooleanField(read_only=True)
    has_comments = serializers.BooleanField(read_only=True)
    latest_comment = serializers.CharField(read_only=True)
    doubled_title_len = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "title",
            "content",
            "image",
            "tags",       
            "tag_ids",    
            "comments",
            "created_at",

            "comment_count",
            "has_image",
            "has_comments",
            "latest_comment",
            "doubled_title_len"
        ]


    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        post = Post.objects.create(author=user, **validated_data)
        if tags:
            post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance
    


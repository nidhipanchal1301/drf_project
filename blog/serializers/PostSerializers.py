from rest_framework import serializers
from ..models import Post, Tag
from .CommentSerializers import CommentSerializer
from .TagSerializers import TagSerializer



class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True, slug_field='username')
    comments = CommentSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        source="tags"
    )

    # analytics fields
    comment_count = serializers.IntegerField(read_only=True)
    has_image = serializers.BooleanField(read_only=True)
    has_comments = serializers.BooleanField(read_only=True)
    latest_comment = serializers.CharField(read_only=True)
    doubled_title_len = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "author", "title", "content", "image", "tags", "tag_ids", "comments", "created_at", "comment_count", 
                  "has_image", "has_comments", "latest_comment", "doubled_title_len",)
        read_only_fields = ["author"]

    def create(self, validated_data):
        tags = validated_data.pop("tags", ())
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

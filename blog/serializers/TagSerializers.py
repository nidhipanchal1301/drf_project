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
        comments = set()

        for post in tag.posts.all():
            for comment in post.comments.all():
                comments.add(comment)

        return CommentSerializer(list(comments), many=True, context=self.context).data

  


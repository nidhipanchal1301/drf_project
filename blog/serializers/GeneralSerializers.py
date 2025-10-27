from rest_framework import serializers


class BasicPostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()

    def create(self, validated_data):
        return {"title": validated_data["title"], "content": validated_data["content"]}

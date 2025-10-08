from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from ..models import Tag
from ..serializers import TagSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all().only("id", "name")
    serializer_class = TagSerializer
    permission_classes = [AllowAny]

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from ..models import User
from ..serializers.UserSerializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"detail": "User soft-deleted"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def upload_profile_image(self, request, pk=None):
        user = self.get_object()
        file_obj = request.FILES.get("profile_image")
        if not file_obj:
            return Response({"detail": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        user.profile_image = file_obj
        user.save()
        return Response(UserSerializer(user, context={"request": request}).data)

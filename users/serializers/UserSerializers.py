from rest_framework import serializers
from ..models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "bio", "profile_image", "phone_number", "gender", "date_of_birth",
            "is_verified", "is_staff", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["is_staff", "is_active", "created_at", "updated_at"]

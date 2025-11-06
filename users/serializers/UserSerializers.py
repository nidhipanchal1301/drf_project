from rest_framework import serializers

from ..models import User

from django.contrib.auth import get_user_model

User = get_user_model()



class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "bio", "profile_image", "phone_number", "gender", "date_of_birth",
            "is_verified", "is_staff", "is_active", "created_at", "updated_at","password",
        ]
        read_only_fields = ["is_staff", "is_active", "created_at", "updated_at"]



    def create(self, validated_data):
        password = validated_data.pop("password", None) 
        user = User(**validated_data)
        if password:  
            user.set_password(password)
        else:
            user.set_password(User.objects.make_random_password())
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    

    # only admins can assign roles
    def validate_role(self, value):
        request = self.context.get("request")
        if request and not (request.user and request.user.is_authenticated and request.user.is_admin):
            raise serializers.ValidationError("Only admins can change role.")
        return value
from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.profiles.models.profile import Profile
from django.db import transaction
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password")
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data["email"],
                email=validated_data["email"],
                password=validated_data["password"],
                is_active=True,
                is_verified=False
            )
            profile = Profile.objects.create(user=user)
        return user

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.profiles.models.profile import Profile
from django.db import transaction
from apps.accounts.services.auth import AuthService
User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    age = serializers.IntegerField(
        min_value=18,
        required=True,
        error_messages={
            "required": "Age is required.",
            "invalid": "Age must be a whole number.",
            "min_value": "You must be at least 18 years old to register.",
        },
    )

    class Meta:
        model = User
        fields = ("email", "password", "confirm_password", "age")
        extra_kwargs = {
            "password": {"write_only": True},
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
                age=validated_data["age"],
                is_active=True,
                is_verified=False
            )
            profile = Profile.objects.create(user=user)
        
        request = self.context.get("request")
        if request:
            AuthService.send_verification_email(user, request)
            
        return user

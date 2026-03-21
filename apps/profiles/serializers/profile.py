from django.utils import timezone
from rest_framework import serializers

from apps.profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "language",
            "difficulty",
            "email",
            "username",
            "lives",
            "streak",
            "max_streak",
            "challenge_day",
            "joined_challenge_at",
            "level",
            "is_rogue",
        )
        read_only_fields = (
            "lives",
            "streak",
            "max_streak",
            "challenge_day",
            "joined_challenge_at",
            "level",
            "is_rogue",
            "email",
            "username",
        )

    def validate(self, data):
        profile = self.instance
        if profile and profile.joined_challenge_at:
            if "language" in data or "difficulty" in data:
                raise serializers.ValidationError(
                    "Cannot change language or difficulty after challenge starts"
                )
        return data

    def update(self, instance, validated_data):
        if (
            "difficulty" in validated_data
            and validated_data["difficulty"] is not None
            and instance.joined_challenge_at is None
        ):
            validated_data["joined_challenge_at"] = timezone.now()
            validated_data["challenge_day"] = 1
            validated_data["last_closed_ist_date"] = None
            validated_data["lives"] = 3
            validated_data["streak"] = 0
            validated_data["max_streak"] = 0
        return super().update(instance, validated_data)



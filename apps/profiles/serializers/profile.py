from rest_framework import serializers
from apps.profiles.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "language",
            "difficulty",
            "lives",
            "streak",
            "max_streak",
            "xp",
            "level",
            "is_rogue",
        )
        read_only_fields = (
            "lives",
            "streak",
            "max_streak",
            "xp",
            "level",
            "is_rogue",
        )

    def validate(self, data):
        profile = self.instance
        if profile and profile.joined_challenge_at:
            if "language" in data or "difficulty" in data:
                raise serializers.ValidationError(
                    "Cannot change language or difficulty after challenge starts"
                )
        return data



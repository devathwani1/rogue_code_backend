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

    def patch(self, request):
        profile = request.user.rogue

        if profile.joined_challenge_at and (
            "language" in request.data or
            "difficulty" in request.data
        ):
            raise serializers.ValidationError(
               "Cannot change language or difficulty after challenge starts"
            )



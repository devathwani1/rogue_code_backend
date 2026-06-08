from rest_framework import serializers

from apps.accounts.models import User


class AdminUserSerializer(serializers.ModelSerializer):
    """Staff-only list: user row + linked profile summary (no password)."""

    language = serializers.SerializerMethodField()
    lives = serializers.SerializerMethodField()
    streak = serializers.SerializerMethodField()
    max_streak = serializers.SerializerMethodField()
    challenge_day = serializers.SerializerMethodField()
    difficulty = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "user_id",
            "email",
            "age",
            "username",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "is_active",
            "is_verified",
            "date_joined",
            "last_login",
            "created_at",
            "language",
            "lives",
            "streak",
            "max_streak",
            "challenge_day",
            "difficulty",
        )

    def _profile(self, obj: User):
        return getattr(obj, "profile", None)

    def get_language(self, obj: User):
        p = self._profile(obj)
        return p.language if p else None

    def get_lives(self, obj: User):
        p = self._profile(obj)
        return p.lives if p else None

    def get_streak(self, obj: User):
        p = self._profile(obj)
        return p.streak if p else None

    def get_max_streak(self, obj: User):
        p = self._profile(obj)
        return p.max_streak if p else None

    def get_challenge_day(self, obj: User):
        p = self._profile(obj)
        return p.challenge_day if p else None

    def get_difficulty(self, obj: User):
        p = self._profile(obj)
        if p and p.difficulty_id:
            return p.difficulty.name
        return None

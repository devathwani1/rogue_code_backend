from rest_framework import serializers

from apps.challenges.models import UserQuestionLastAttempt


class UserQuestionLastAttemptSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(source="question.id", read_only=True)
    title = serializers.CharField(source="question.title", read_only=True)
    slug = serializers.SlugField(source="question.slug", read_only=True)
    difficulty = serializers.CharField(source="question.difficulty", read_only=True)

    class Meta:
        model = UserQuestionLastAttempt
        fields = (
            "question_id",
            "title",
            "slug",
            "difficulty",
            "last_attempted_at",
            "last_success",
            "last_passed",
            "last_total",
        )

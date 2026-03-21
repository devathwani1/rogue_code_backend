from __future__ import annotations

from rest_framework import serializers

from apps.challenges.models import DailyPlanItemSolve


class AdminSubmissionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    question_id = serializers.UUIDField(source="daily_plan_item.question_id", read_only=True)
    question_title = serializers.CharField(source="daily_plan_item.question.title", read_only=True)
    question_slug = serializers.SlugField(source="daily_plan_item.question.slug", read_only=True)
    question_difficulty = serializers.CharField(
        source="daily_plan_item.question.difficulty", read_only=True
    )
    day_number = serializers.IntegerField(
        source="daily_plan_item.daily_plan.day_number", read_only=True
    )
    plan_difficulty = serializers.SerializerMethodField()
    item_order = serializers.IntegerField(source="daily_plan_item.order", read_only=True)

    class Meta:
        model = DailyPlanItemSolve
        fields = (
            "id",
            "user_id",
            "user_email",
            "user_username",
            "question_id",
            "question_title",
            "question_slug",
            "question_difficulty",
            "day_number",
            "plan_difficulty",
            "item_order",
            "passed",
            "total",
            "success",
            "last_submitted_at",
            "created_at",
        )

    def get_plan_difficulty(self, obj: DailyPlanItemSolve) -> str | None:
        qp = obj.daily_plan_item.daily_plan.question_plan
        d = qp.difficulty
        return d.name if d else None

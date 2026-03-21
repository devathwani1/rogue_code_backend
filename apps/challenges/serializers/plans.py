from rest_framework import serializers

from apps.challenges.models import DailyPlan, DailyPlanItem, DailyPlanItemSolve


class DailyPlanSerializer(serializers.ModelSerializer):
    """
    status: Success | Failed (day closed via rollover), Current (active day),
    Upcoming (not reached yet).
    """

    status = serializers.SerializerMethodField()

    class Meta:
        model = DailyPlan
        fields = ("id", "day_number", "status")

    def get_status(self, obj: DailyPlan) -> str:
        profile = self.context.get("profile")
        solves_map: dict = self.context.get("solves_by_plan_id") or {}
        if profile is None:
            return "Upcoming"

        solve = solves_map.get(obj.pk)
        if solve is not None:
            return "Success" if solve.success else "Failed"

        if obj.day_number == profile.challenge_day:
            return "Current"
        if obj.day_number > profile.challenge_day:
            return "Upcoming"
        # Past day_number without a solve row (should be rare): treat as failed.
        return "Failed"


class DailyPlanItemSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="question.id")
    title = serializers.CharField(source="question.title")
    difficulty = serializers.CharField(source="question.difficulty")
    status = serializers.SerializerMethodField()

    class Meta:
        model = DailyPlanItem
        fields = ("id", "title", "difficulty", "order", "status")

    def get_status(self, obj: DailyPlanItem) -> str:
        solve_map: dict = self.context.get("item_solve_map") or {}
        if solve_map:
            solve = solve_map.get(obj.pk)
        else:
            request = self.context.get("request")
            user = getattr(request, "user", None) if request else None
            if not user or not user.is_authenticated:
                return "Pending"
            solve = DailyPlanItemSolve.objects.filter(
                user=user,
                daily_plan_item=obj,
            ).first()
        if not solve:
            return "Pending"
        return "Completed" if solve.success else "Failed"

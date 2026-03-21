from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.challenges.models import DailyPlan, DailyPlanItem, DailyPlanItemSolve, QuestionPlan


class DailyProgressService:
    @staticmethod
    def record_question_solve(
        user,
        *,
        question_id,
        passed: int,
        total: int,
        success: bool,
    ) -> None:
        """
        Persists solve status for the user's daily plan items that match `question_id`.
        """
        profile = getattr(user, "profile", None)
        if not profile or not profile.difficulty:
            return

        question_plan = (
            QuestionPlan.objects.filter(difficulty=profile.difficulty, is_active=True).first()
        )
        if not question_plan:
            return

        daily_items = DailyPlanItem.objects.filter(
            question_id=question_id,
            daily_plan__question_plan=question_plan,
        )

        for item in daily_items:
            existing = DailyPlanItemSolve.objects.filter(
                user=user,
                daily_plan_item=item,
            ).first()

            if existing and existing.success:
                # Preserve the "solved" state even if the user submits a wrong solution later.
                continue

            DailyPlanItemSolve.objects.update_or_create(
                user=user,
                daily_plan_item=item,
                defaults={
                    "passed": passed,
                    "total": total,
                    "success": success,
                },
            )

    @staticmethod
    def recompute_profile_progress(user) -> None:
        """
        Updates last_completed_at when the user's current challenge_day daily plan
        is fully solved. Streak / challenge_day / lives are owned by the IST
        day-close job (DayRolloverService).
        """
        profile = getattr(user, "profile", None)
        if not profile or not profile.difficulty or not profile.joined_challenge_at:
            return

        question_plan = (
            QuestionPlan.objects.filter(difficulty=profile.difficulty, is_active=True).first()
        )
        if not question_plan:
            return

        daily_plan = DailyPlan.objects.filter(
            question_plan=question_plan,
            day_number=profile.challenge_day,
        ).first()
        if not daily_plan:
            return

        items_qs = DailyPlanItem.objects.filter(daily_plan=daily_plan)
        total_items = items_qs.count()
        if total_items == 0:
            return

        solved_items = (
            DailyPlanItemSolve.objects.filter(
                user=user,
                daily_plan_item__in=items_qs,
                success=True,
            )
            .values("daily_plan_item_id")
            .distinct()
            .count()
        )

        if solved_items == total_items:
            profile.last_completed_at = timezone.now()
            profile.save(update_fields=["last_completed_at"])


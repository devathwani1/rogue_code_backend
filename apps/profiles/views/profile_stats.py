from __future__ import annotations

from django.db.models import Count

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.challenges.models import DailyPlanItemSolve, DailyPlanSolve, QuestionPlan
from apps.challenges.services.day_rollover_service import DayRolloverService
from apps.profiles.models import Profile


class ProfileStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        DayRolloverService.process_user(user)
        profile: Profile = user.profile
        profile.refresh_from_db()

        difficulty = profile.difficulty
        total_days = int(difficulty.days) if difficulty else 0
        total_questions = int(difficulty.number_of_questions) if difficulty else 0

        solved_qs = DailyPlanItemSolve.objects.filter(user=user, success=True)
        solved_count = (
            solved_qs.values("daily_plan_item_id").distinct().count()
        )

        solved_by_diff_rows = (
            solved_qs.values("daily_plan_item__question__difficulty")
            .annotate(n=Count("pk", distinct=False))
        )
        solved_easy = 0
        solved_medium = 0
        solved_hard = 0
        for row in solved_by_diff_rows:
            key = row["daily_plan_item__question__difficulty"] or ""
            n = int(row["n"])
            if key == "easy":
                solved_easy = n
            elif key == "medium":
                solved_medium = n
            elif key == "hard":
                solved_hard = n

        max_cores = 3
        available_cores = int(profile.lives)
        survived_days = int(profile.streak)
        max_streak = int(profile.max_streak)

        solved_percent = 0
        if total_questions > 0:
            solved_percent = round((solved_count / total_questions) * 100, 2)

        day_results = []
        qp = None
        if difficulty:
            qp = QuestionPlan.objects.filter(difficulty=difficulty, is_active=True).first()
        if qp:
            qs = (
                DailyPlanSolve.objects.filter(user=user, daily_plan__question_plan=qp)
                .select_related("daily_plan")
                .order_by("daily_plan__day_number")
            )
            day_results = [
                {
                    "day_number": s.daily_plan.day_number,
                    "success": s.success,
                    "closed_at": s.closed_at.isoformat() if s.closed_at else None,
                }
                for s in qs
            ]

        return Response(
            {
                "email": getattr(user, "email", ""),
                "username": getattr(user, "username", ""),
                "language": profile.language,
                "difficulty": getattr(difficulty, "name", None),
                "lives": available_cores,
                "max_lives": max_cores,
                "streak": survived_days,
                "max_streak": max_streak,
                "challenge_day": profile.challenge_day,
                "total_days": total_days,
                "solved": solved_count,
                "total_questions": total_questions,
                "solved_percent": solved_percent,
                "solved_easy": solved_easy,
                "solved_medium": solved_medium,
                "solved_hard": solved_hard,
                "day_results": day_results,
            }
        )


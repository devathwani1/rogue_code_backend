from django.conf import settings
from django.db import models

from .plans import DailyPlan, DailyPlanItem


class DailyPlanItemSolve(models.Model):
    """
    Stores whether a user has successfully solved a specific DailyPlanItem.
    Used to compute day-wise completion (and therefore profile.streak unlocking).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_plan_item_solves",
    )
    daily_plan_item = models.ForeignKey(
        DailyPlanItem,
        on_delete=models.CASCADE,
        related_name="solves",
    )

    passed = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    success = models.BooleanField(default=False)

    last_submitted_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "daily_plan_item")
        ordering = ["-last_submitted_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.daily_plan_item_id} success={self.success}"


class DailyPlanSolve(models.Model):
    """
    Canonical pass/fail for a full calendar challenge day (one row per user × DailyPlan),
    written when the IST day is closed (midnight rollover job).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_plan_solves",
    )
    daily_plan = models.ForeignKey(
        DailyPlan,
        on_delete=models.CASCADE,
        related_name="solves",
    )
    success = models.BooleanField(default=False)
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "daily_plan"),
                name="uniq_user_daily_plan_solve",
            )
        ]
        ordering = ["daily_plan__day_number"]

    def __str__(self) -> str:
        return f"{self.user_id}:day{self.daily_plan.day_number} success={self.success}"


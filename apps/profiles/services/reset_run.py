"""
Full challenge run reset after all lives are lost (3 → 0).

Clears per-user daily progress rows and restores profile counters so the user
can start again from day 1 on the same difficulty/language.
"""

from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.challenges.models import DailyPlanItemSolve, DailyPlanSolve, UserQuestionLastAttempt
from apps.challenges.services.day_rollover_service import _ist_date
from apps.profiles.models import Profile


class ResetRunError(Exception):
    """Business rule blocked reset (e.g. lives not zero)."""


def reset_user_run(user) -> Profile:
    """
    Delete all DailyPlanItemSolve / DailyPlanSolve for ``user`` and reset profile
    streak/cores/day counters. Only allowed when ``profile.lives == 0``.
    """
    with transaction.atomic():
        profile = Profile.objects.select_for_update().get(user=user)
        if profile.lives != 0:
            raise ResetRunError(
                "Progress can only be wiped after all cores are lost (lives must be 0)."
            )
        if not profile.joined_challenge_at:
            raise ResetRunError("You have not started a challenge run yet.")

        DailyPlanItemSolve.objects.filter(user=user).delete()
        DailyPlanSolve.objects.filter(user=user).delete()
        UserQuestionLastAttempt.objects.filter(user=user).delete()

        profile.lives = 3
        profile.streak = 0
        profile.max_streak = 0
        profile.challenge_day = 1
        # Align IST calendar so DayRolloverService does not "catch up" from join_date
        # and immediately burn lives (empty days would count as failed). Setting this to
        # **yesterday IST** makes start_close = today IST > end_ist (yesterday) → no close.
        profile.last_closed_ist_date = _ist_date(timezone.now()) - timedelta(days=1)
        profile.last_completed_at = None
        profile.level = 1
        profile.is_rogue = False
        profile.save(
            update_fields=[
                "lives",
                "streak",
                "max_streak",
                "challenge_day",
                "last_closed_ist_date",
                "last_completed_at",
                "level",
                "is_rogue",
            ]
        )
    return profile

"""
IST calendar day close: create DailyPlanSolve, adjust lives/streak/challenge_day.

Run periodically (e.g. cron after midnight IST) via management command.

By default we only close through **yesterday** IST so "today" can still be played.
"""
from __future__ import annotations

from collections.abc import Callable
from datetime import date, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from apps.challenges.models import (
    DailyPlan,
    DailyPlanItem,
    DailyPlanItemSolve,
    DailyPlanSolve,
    QuestionPlan,
)
from apps.profiles.models import Profile

IST = ZoneInfo("Asia/Kolkata")


def _ist_date(dt) -> date:
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, IST)
    return dt.astimezone(IST).date()


def _iter_dates(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def _day_success(user, daily_plan: DailyPlan) -> bool:
    items = DailyPlanItem.objects.filter(daily_plan=daily_plan)
    total = items.count()
    if total == 0:
        return False
    solved = (
        DailyPlanItemSolve.objects.filter(
            user=user,
            daily_plan_item__in=items,
            success=True,
        )
        .values("daily_plan_item_id")
        .distinct()
        .count()
    )
    return solved == total


def _backfill_unattempted_item_solves(user, daily_plan: DailyPlan) -> int:
    """
    When a calendar day is closed, ensure every DailyPlanItem has a row for this user.
    Items never submitted get DailyPlanItemSolve(success=False, passed=0, total=0).
    Existing rows (any success value) are left unchanged.
    """
    items = list(DailyPlanItem.objects.filter(daily_plan=daily_plan))
    if not items:
        return 0
    existing = set(
        DailyPlanItemSolve.objects.filter(
            user=user,
            daily_plan_item__in=items,
        ).values_list("daily_plan_item_id", flat=True)
    )
    n = 0
    for item in items:
        if item.pk in existing:
            continue
        DailyPlanItemSolve.objects.create(
            user=user,
            daily_plan_item=item,
            passed=0,
            total=0,
            success=False,
        )
        n += 1
    return n


def _challenge_fully_recorded(user, question_plan: QuestionPlan) -> bool:
    plan_days = DailyPlan.objects.filter(question_plan=question_plan).count()
    if plan_days == 0:
        return False
    done = DailyPlanSolve.objects.filter(
        user=user,
        daily_plan__question_plan=question_plan,
    ).count()
    return done >= plan_days


def _apply_single_day_close(
    user,
    profile: Profile,
    *,
    daily_plan: DailyPlan,
    max_day: int,
    last_closed_ist_date: date,
    log: Optional[Callable[[str], None]] = None,
) -> None:
    """Mutates and saves ``profile``: DailyPlanSolve, item backfill, lives/streak/challenge_day."""
    def trace(msg: str) -> None:
        if log:
            log(msg)

    success = _day_success(user, daily_plan)

    backfilled = _backfill_unattempted_item_solves(user, daily_plan)
    if backfilled and log:
        trace(
            f"user={user.pk} plan_day={daily_plan.day_number} backfilled {backfilled} "
            f"unattempted DailyPlanItemSolve (success=False)"
        )

    DailyPlanSolve.objects.update_or_create(
        user=user,
        daily_plan=daily_plan,
        defaults={"success": success},
    )

    if not success:
        profile.lives = max(0, profile.lives - 1)
        profile.streak = 0
    else:
        profile.streak = profile.streak + 1
        if profile.streak > (profile.max_streak or 0):
            profile.max_streak = profile.streak

    profile.challenge_day = min(profile.challenge_day + 1, max_day)
    profile.last_closed_ist_date = last_closed_ist_date
    profile.save(
        update_fields=[
            "lives",
            "streak",
            "max_streak",
            "challenge_day",
            "last_closed_ist_date",
        ]
    )
    trace(
        f"user={user.pk} closed plan_day={daily_plan.day_number} success={success} "
        f"-> challenge_day={profile.challenge_day} lives={profile.lives} streak={profile.streak} "
        f"last_closed_ist_date={last_closed_ist_date}"
    )


class DayRolloverService:
    @staticmethod
    def process_user(
        user,
        *,
        now=None,
        include_today: bool = False,
        log: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        Close IST calendar days from (last_closed + 1) through **end_ist**.

        Default ``end_ist`` is **yesterday** in Asia/Kolkata (today is still open).

        Set ``include_today=True`` only for **local/testing** to treat today's IST
        date as already finished (not for production cron).
        """
        def trace(msg: str) -> None:
            if log:
                log(msg)

        now = now or timezone.now()
        profile: Profile | None = getattr(user, "profile", None)
        if not profile or not profile.joined_challenge_at or not profile.difficulty:
            trace(f"skip user={getattr(user, 'pk', '?')}: no profile / not joined / no difficulty")
            return 0

        question_plan = QuestionPlan.objects.filter(
            difficulty=profile.difficulty,
            is_active=True,
        ).first()

        if not question_plan:
            trace(f"skip user={user.pk}: no active QuestionPlan")
            return 0

        max_day = (
            DailyPlan.objects.filter(question_plan=question_plan).aggregate(
                m=Max("day_number")
            )["m"]
            or 0
        )
        if max_day == 0:
            trace(f"skip user={user.pk}: no DailyPlan rows")
            return 0

        join_date = _ist_date(profile.joined_challenge_at)
        today_ist = _ist_date(now)
        yesterday_ist = today_ist - timedelta(days=1)
        end_ist = today_ist if include_today else yesterday_ist

        if end_ist < join_date:
            trace(
                f"skip user={user.pk}: end_ist={end_ist} < join_date={join_date} "
                f"(no full IST day to close yet)"
            )
            return 0

        start_close = join_date
        if profile.last_closed_ist_date:
            start_close = profile.last_closed_ist_date + timedelta(days=1)

        if start_close > end_ist:
            trace(
                f"skip user={user.pk}: already closed through end_ist={end_ist} "
                f"(start_close={start_close})"
            )
            return 0

        trace(
            f"user={user.pk} close window IST: {start_close} .. {end_ist} "
            f"(today_ist={today_ist}, include_today={include_today}, "
            f"challenge_day={profile.challenge_day})"
        )

        processed = 0

        with transaction.atomic():
            profile = Profile.objects.select_for_update().get(pk=profile.pk)

            if _challenge_fully_recorded(user, question_plan):
                profile.last_closed_ist_date = end_ist
                profile.save(update_fields=["last_closed_ist_date"])
                n_calendar = max(0, (end_ist - start_close).days + 1)
                trace(
                    f"user={user.pk}: challenge fully recorded; "
                    f"calendar catch-up last_closed_ist_date={end_ist} ({n_calendar} IST day span)"
                )
                return n_calendar

            for ist_day in _iter_dates(start_close, end_ist):
                if _challenge_fully_recorded(user, question_plan):
                    profile.last_closed_ist_date = end_ist
                    profile.save(update_fields=["last_closed_ist_date"])
                    trace(f"user={user.pk}: mid-loop full; catch-up last_closed={end_ist}")
                    break

                daily_plan = DailyPlan.objects.filter(
                    question_plan=question_plan,
                    day_number=profile.challenge_day,
                ).first()
                if not daily_plan:
                    trace(
                        f"user={user.pk}: stop ist_day={ist_day} no DailyPlan for "
                        f"challenge_day={profile.challenge_day}"
                    )
                    break

                _apply_single_day_close(
                    user,
                    profile,
                    daily_plan=daily_plan,
                    max_day=max_day,
                    last_closed_ist_date=ist_day,
                    log=log,
                )
                processed += 1

        trace(f"user={user.pk}: done, game_closes_applied={processed}")
        return processed

    @staticmethod
    def force_close_current_challenge_day(
        user,
        *,
        now=None,
        log: Optional[Callable[[str], None]] = None,
    ) -> int:
        """
        TEST ONLY: close exactly the user's current ``challenge_day`` once.

        Ignores IST join / last_closed / yesterday–today windows. Sets
        ``last_closed_ist_date`` to **today (IST)** so normal rollover stays roughly aligned.

        Returns ``1`` if a day was closed, ``0`` otherwise.
        """
        def trace(msg: str) -> None:
            if log:
                log(msg)

        now = now or timezone.now()
        today_ist = _ist_date(now)
        profile: Profile | None = getattr(user, "profile", None)
        if not profile or not profile.joined_challenge_at or not profile.difficulty:
            trace(f"force_close skip user={getattr(user, 'pk', '?')}: not joined / no difficulty")
            return 0

        question_plan = QuestionPlan.objects.filter(
            difficulty=profile.difficulty,
            is_active=True,
        ).first()
        if not question_plan:
            trace(f"force_close skip user={user.pk}: no active QuestionPlan")
            return 0

        max_day = (
            DailyPlan.objects.filter(question_plan=question_plan).aggregate(
                m=Max("day_number")
            )["m"]
            or 0
        )
        if max_day == 0:
            trace(f"force_close skip user={user.pk}: no DailyPlan rows")
            return 0

        with transaction.atomic():
            profile = Profile.objects.select_for_update().get(pk=profile.pk)

            if _challenge_fully_recorded(user, question_plan):
                trace(
                    f"force_close skip user={user.pk}: all plan days already have DailyPlanSolve"
                )
                return 0

            daily_plan = DailyPlan.objects.filter(
                question_plan=question_plan,
                day_number=profile.challenge_day,
            ).first()
            if not daily_plan:
                trace(
                    f"force_close skip user={user.pk}: no DailyPlan for "
                    f"challenge_day={profile.challenge_day}"
                )
                return 0

            trace(
                f"force_close user={user.pk} challenge_day={profile.challenge_day} "
                f"-> daily_plan day_number={daily_plan.day_number} (IST today={today_ist}, dates ignored)"
            )
            _apply_single_day_close(
                user,
                profile,
                daily_plan=daily_plan,
                max_day=max_day,
                last_closed_ist_date=today_ist,
                log=log,
            )

        return 1

    @staticmethod
    def force_close_current_challenge_day_all_users(
        *,
        now=None,
        log: Optional[Callable[[str], None]] = None,
    ) -> int:
        total = 0
        qs = Profile.objects.filter(joined_challenge_at__isnull=False).select_related(
            "user", "difficulty"
        )
        for profile in qs.iterator():
            total += DayRolloverService.force_close_current_challenge_day(
                profile.user,
                now=now,
                log=log,
            )
        return total

    @staticmethod
    def process_all_users(
        *,
        now=None,
        include_today: bool = False,
        log: Optional[Callable[[str], None]] = None,
    ) -> int:
        """Run process_user for every profile that has started the challenge."""
        total = 0
        qs = Profile.objects.filter(joined_challenge_at__isnull=False).select_related(
            "user", "difficulty"
        )
        for profile in qs.iterator():
            total += DayRolloverService.process_user(
                profile.user,
                now=now,
                include_today=include_today,
                log=log,
            )
        return total

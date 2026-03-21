from django.core.management.base import BaseCommand

from apps.challenges.services.day_rollover_service import DayRolloverService


class Command(BaseCommand):
    help = (
        "Close IST calendar days for all users who joined the challenge: "
        "writes DailyPlanSolve, updates lives/streak/challenge_day. "
        "Schedule after midnight IST (e.g. cron).\n\n"
        "Use --force-current-day only in dev: closes the user's current challenge_day once "
        "and ignores IST date windows (not for production)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="Only process this user id (for debugging).",
        )
        parser.add_argument(
            "--include-today",
            action="store_true",
            help=(
                "Also close today's IST date (for local testing). "
                "Production cron should NOT use this — wait until after midnight IST."
            ),
        )
        parser.add_argument(
            "--force-current-day",
            action="store_true",
            help=(
                "TEST ONLY: close exactly the current plan day (profile.challenge_day) once, "
                "ignoring join date and last_closed_ist_date completely. "
                "Sets last_closed_ist_date to today (IST). "
                "Does not run normal IST window rollover in the same invocation."
            ),
        )

    def handle(self, *args, **options):
        verbosity = options.get("verbosity", 1)
        log = self.stdout.write if verbosity >= 2 else None
        include_today = options.get("include_today", False)
        force_current = options.get("force_current_day", False)
        uid = options.get("user_id")

        if force_current and include_today:
            self.stdout.write(
                self.style.WARNING(
                    "--include-today is ignored when --force-current-day is set."
                )
            )

        if force_current:
            if uid:
                from django.contrib.auth import get_user_model

                User = get_user_model()
                user = User.objects.get(pk=uid)
                n = DayRolloverService.force_close_current_challenge_day(
                    user,
                    log=log,
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Force-close current plan day for user {uid}: "
                        f"{'applied 1 close' if n else 'nothing done (see -v 2)'}"
                    )
                )
                return

            n = DayRolloverService.force_close_current_challenge_day_all_users(log=log)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Force-close current plan day for all joined users: {n} close(s) applied."
                )
            )
            return

        if uid:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            user = User.objects.get(pk=uid)
            n = DayRolloverService.process_user(
                user,
                include_today=include_today,
                log=log,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Processed {n} IST day(s) for user {uid}.")
            )
            return

        total = DayRolloverService.process_all_users(
            include_today=include_today,
            log=log,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished day rollover (aggregate IST steps: {total})."
            )
        )

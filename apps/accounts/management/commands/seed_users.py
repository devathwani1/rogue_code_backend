import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from apps.challenges.models import DailyPlanItem, DailyPlanItemSolve
from apps.common.models import Difficulty
from apps.profiles.models.profile import Profile


SEED_USER_COUNT = 10
SEED_PASSWORD = "temp@123"


class Command(BaseCommand):
    help = "Seed realistic demo users with random profile and progress data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=SEED_USER_COUNT,
            help="Number of users to create (default: 10).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()
        user_model = get_user_model()
        difficulties = list(Difficulty.objects.all())
        languages = [choice[0] for choice in Profile.Language.choices]
        created_count = 0
        count = max(1, int(options["count"]))

        for _ in range(count):
            email = fake.unique.email().lower()
            username = email
            first_name = fake.first_name()
            last_name = fake.last_name()

            user = user_model.objects.create_user(
                username=username,
                email=email,
                password=SEED_PASSWORD,
                is_active=True,
                is_verified=True,
                first_name=first_name,
                last_name=last_name,
            )
            created_count += 1

            streak = random.randint(0, 20)
            profile = Profile.objects.create(
                user=user,
                language=random.choice(languages),
                difficulty=random.choice(difficulties) if difficulties else None,
                streak=streak,
                max_streak=random.randint(max(1, streak), 40),
                challenge_day=random.randint(1, 15),
                lives=random.randint(1, 3),
                level=random.randint(1, 12),
                is_rogue=random.choice([True, False]),
            )

            if profile.difficulty:
                items_qs = DailyPlanItem.objects.filter(
                    daily_plan__question_plan__difficulty=profile.difficulty,
                    daily_plan__question_plan__is_active=True,
                ).select_related("daily_plan", "question")
                items = list(items_qs)
                if items:
                    solved_count = random.randint(1, min(8, len(items)))
                    solved_items = random.sample(items, solved_count)
                    for item in solved_items:
                        total_cases = item.question.test_cases.count() or 1
                        passed = random.randint(0, total_cases)
                        DailyPlanItemSolve.objects.update_or_create(
                            user=user,
                            daily_plan_item=item,
                            defaults={
                                "passed": passed,
                                "total": total_cases,
                                "success": passed == total_cases and total_cases > 0,
                            },
                        )

        self.stdout.write(self.style.SUCCESS("Seed users command completed."))
        self.stdout.write(f"Created users: {created_count}")
        self.stdout.write(f"Password for all seeded users: {SEED_PASSWORD}")

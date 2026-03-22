"""
Replace all challenge questions, test cases, parameters, and question plans with the
v2 curriculum (45 problems; Low/Standard 5-day plans, Crushing 15-day full track).

Usage:
  python manage.py reset_and_seed_questions

Requires: Django shell / DB configured. Destructive for challenges.* tables listed below.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.challenges.data.challenge_seed_v2 import (
    CHALLENGE_QUESTIONS,
    DIFFICULTY_DB_FIELDS,
    EASY_PLAN_DAYS,
    HARD_PLAN_DAYS,
    MEDIUM_PLAN_DAYS,
)
from apps.challenges.models import (
    DailyPlan,
    DailyPlanItem,
    DailyPlanItemSolve,
    DailyPlanSolve,
    Question,
    QuestionParameter,
    QuestionPlan,
    TestCase,
    UserQuestionLastAttempt,
)
from apps.common.models import Difficulty


def _get_difficulty_or_raise(name: str) -> Difficulty:
    try:
        return Difficulty.objects.get(name=name)
    except Difficulty.DoesNotExist as e:
        raise SystemExit(
            f"Difficulty {name!r} not found. Load common.difficulty fixtures or create the row."
        ) from e


class Command(BaseCommand):
    help = "Delete existing questions/plans and seed 15 problems with 5-day plans per tier."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-input",
            action="store_true",
            help="Skip confirmation prompt (for scripts).",
        )

    def handle(self, *args, **options):
        if not options["no_input"]:
            confirm = input(
                "This will DELETE all questions, plans, and related progress rows. Type YES: "
            )
            if confirm.strip() != "YES":
                self.stdout.write(self.style.WARNING("Aborted."))
                return

        with transaction.atomic():
            self._purge()
            self._update_difficulties()
            questions = self._create_questions()
            self._create_plans(questions)

        self.stdout.write(self.style.SUCCESS("Seeded 45 questions and tier question plans."))

    def _purge(self) -> None:
        DailyPlanItemSolve.objects.all().delete()
        DailyPlanSolve.objects.all().delete()
        DailyPlanItem.objects.all().delete()
        DailyPlan.objects.all().delete()
        QuestionPlan.objects.all().delete()
        UserQuestionLastAttempt.objects.all().delete()
        TestCase.objects.all().delete()
        QuestionParameter.objects.all().delete()
        Question.objects.all().delete()

    def _update_difficulties(self) -> None:
        for name, fields in DIFFICULTY_DB_FIELDS.items():
            updated = Difficulty.objects.filter(name=name).update(**fields)
            if not updated:
                self.stdout.write(
                    self.style.WARNING(
                        f"No Difficulty row named {name!r}; create it in admin or fixtures."
                    )
                )

    def _create_questions(self) -> list[Question]:
        created: list[Question] = []
        for spec in CHALLENGE_QUESTIONS:
            q = Question.objects.create(
                title=spec["title"],
                description=spec["description"],
                constraints=spec["constraints"],
                function_name=spec["function_name"],
                return_type=spec["return_type"],
                difficulty=spec["difficulty"],
            )
            for p in spec["parameters"]:
                QuestionParameter.objects.create(
                    question=q,
                    name=p["name"],
                    type_schema=p["type_schema"],
                    order=p["order"],
                )
            for tc in spec["test_cases"]:
                TestCase.objects.create(
                    question=q,
                    input_data=tc["input_data"],
                    expected_output=tc["expected_output"],
                    is_hidden=False,
                )
            created.append(q)
        return created

    def _create_plans(self, questions: list[Question]) -> None:
        """
        One QuestionPlan per tier (Low / Standard / Crushing), each with 5 DailyPlans
        and DailyPlanItems pointing at questions by index.
        """
        layouts = [
            ("Low", EASY_PLAN_DAYS),
            ("Standard", MEDIUM_PLAN_DAYS),
            ("Crushing", HARD_PLAN_DAYS),
        ]
        for tier_name, day_layout in layouts:
            diff = _get_difficulty_or_raise(tier_name)
            qp = QuestionPlan.objects.create(difficulty=diff, is_active=True)
            for day_number, indices in day_layout:
                dp = DailyPlan.objects.create(question_plan=qp, day_number=day_number)
                for order, qidx in enumerate(indices, start=1):
                    DailyPlanItem.objects.create(
                        daily_plan=dp,
                        question=questions[qidx],
                        order=order,
                    )

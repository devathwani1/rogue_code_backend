import uuid
from django.db import models
from apps.common.models import Difficulty
from apps.challenges.models.questions import Question

class QuestionPlan(models.Model):
    difficulty = models.ForeignKey(
        Difficulty,
        on_delete=models.CASCADE,
        related_name="plans"
    )
    version = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Plan {self.version} - {self.difficulty.name}"


class DailyPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_plan = models.ForeignKey(
        QuestionPlan,
        on_delete=models.CASCADE,
        related_name="daily_plans"
    )
    day_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ("question_plan", "day_number")
        ordering = ["day_number"]

    def __str__(self):
        return f"Day {self.day_number} - {self.question_plan}"


class DailyPlanItem(models.Model):
    daily_plan = models.ForeignKey(
        DailyPlan,
        on_delete=models.CASCADE,
        related_name="items"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("daily_plan", "question")
        ordering = ["order"]

    def __str__(self):
        return f"Item {self.order} - {self.question.title} (Day {self.daily_plan.day_number} (Difficulty: {self.daily_plan.question_plan.difficulty.name}))"

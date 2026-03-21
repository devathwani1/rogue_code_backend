from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.challenges.models.questions import Question


class UserQuestionLastAttempt(models.Model):
    """
    Latest submission metadata per (user, question), updated on every code submit.
    Used for "recently attempted questions" independent of daily-plan rows.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="question_last_attempts",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_last_attempts",
    )
    last_attempted_at = models.DateTimeField(db_index=True)
    last_success = models.BooleanField(default=False)
    last_passed = models.PositiveSmallIntegerField(default=0)
    last_total = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "question"),
                name="uniq_user_question_last_attempt",
            )
        ]
        ordering = ["-last_attempted_at"]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.question_id} @ {self.last_attempted_at}"

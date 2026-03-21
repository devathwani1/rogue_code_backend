# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("challenges", "0008_dailyplansolve"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserQuestionLastAttempt",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_attempted_at", models.DateTimeField(db_index=True)),
                ("last_success", models.BooleanField(default=False)),
                ("last_passed", models.PositiveSmallIntegerField(default=0)),
                ("last_total", models.PositiveSmallIntegerField(default=0)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_last_attempts",
                        to="challenges.question",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="question_last_attempts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-last_attempted_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="userquestionlastattempt",
            constraint=models.UniqueConstraint(
                fields=("user", "question"),
                name="uniq_user_question_last_attempt",
            ),
        ),
    ]

# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("challenges", "0007_remove_questionplan_version"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyPlanSolve",
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
                ("success", models.BooleanField(default=False)),
                ("closed_at", models.DateTimeField(auto_now_add=True)),
                (
                    "daily_plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="solves",
                        to="challenges.dailyplan",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_plan_solves",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["daily_plan__day_number"],
            },
        ),
        migrations.AddConstraint(
            model_name="dailyplansolve",
            constraint=models.UniqueConstraint(
                fields=("user", "daily_plan"),
                name="uniq_user_daily_plan_solve",
            ),
        ),
    ]

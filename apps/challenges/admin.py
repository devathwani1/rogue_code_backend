from django.contrib import admin
from apps.challenges.models.questions import Question
from apps.challenges.models.parameters import QuestionParameter
from apps.challenges.models.test_case import TestCase
from apps.challenges.models.plans import QuestionPlan, DailyPlan, DailyPlanItem
from apps.challenges.models.progress import DailyPlanItemSolve, DailyPlanSolve


@admin.register(DailyPlanItemSolve)
class DailyPlanItemSolveAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "daily_plan_item",
        "passed",
        "total",
        "success",
        "last_submitted_at",
    )
    list_filter = ("success",)
    search_fields = ("user__username", "user__email", "daily_plan_item__question__title")
    raw_id_fields = ("user", "daily_plan_item")
    readonly_fields = ("last_submitted_at", "created_at")
    ordering = ("-last_submitted_at",)


admin.site.register(Question)
admin.site.register(QuestionParameter)
admin.site.register(TestCase)
admin.site.register(QuestionPlan)
admin.site.register(DailyPlan)
admin.site.register(DailyPlanItem)
admin.site.register(DailyPlanSolve)

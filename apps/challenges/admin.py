from django.contrib import admin
from apps.challenges.models.questions import Question
from apps.challenges.models.parameters import QuestionParameter
from apps.challenges.models.test_case import TestCase
from apps.challenges.models.plans import QuestionPlan, DailyPlan, DailyPlanItem

admin.site.register(Question)
admin.site.register(QuestionParameter)
admin.site.register(TestCase)
admin.site.register(QuestionPlan)
admin.site.register(DailyPlan)
admin.site.register(DailyPlanItem)

from apps.challenges.views.questions import QuestionListView, QuestionDetailView, QuestionSolveView
from apps.challenges.views.plans import DailyPlanListView, DailyPlanItemListView
from django.urls import path

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/<uuid:question_id>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<uuid:question_id>/solve/', QuestionSolveView.as_view(), name='question-solve'),
    path('daily-plans/', DailyPlanListView.as_view(), name='daily-plan-list'),
    path('daily-plans/<uuid:daily_plan_id>/items/', DailyPlanItemListView.as_view(), name='daily-plan-item-list'),
]

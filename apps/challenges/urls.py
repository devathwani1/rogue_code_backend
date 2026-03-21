from apps.challenges.views.questions import (
    AdminQuestionListView,
    QuestionListView,
    QuestionDetailView,
    QuestionSolveView,
    RecentQuestionAttemptsView,
)
from apps.challenges.views.admin_submissions import AdminSubmissionListView
from apps.challenges.views.plans import DailyPlanListView, DailyPlanItemListView
from apps.evaluator.views.submit_code import SubmitSolutionView
from django.urls import path

urlpatterns = [
    path(
        "admin/questions/",
        AdminQuestionListView.as_view(),
        name="admin-question-list",
    ),
    path(
        "admin/submissions/",
        AdminSubmissionListView.as_view(),
        name="admin-submission-list",
    ),
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path(
        'questions/recent/',
        RecentQuestionAttemptsView.as_view(),
        name='question-recent-attempts',
    ),
    path('questions/<uuid:question_id>/', QuestionDetailView.as_view(), name='question-detail'),
    path('questions/<uuid:question_id>/solve/', QuestionSolveView.as_view(), name='question-solve'),
    path('submit/', SubmitSolutionView.as_view(), name='submit-solution'),
    path('daily-plans/', DailyPlanListView.as_view(), name='daily-plan-list'),
    path('daily-plans/<uuid:daily_plan_id>/items/', DailyPlanItemListView.as_view(), name='daily-plan-item-list'),
]

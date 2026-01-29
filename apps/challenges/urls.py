from django.urls import path
from apps.challenges.views.questions import QuestionListView, QuestionDetailView

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/<slug:slug>/', QuestionDetailView.as_view(), name='question-detail'),
]

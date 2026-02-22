from django.urls import path
from .views import DifficultyListView

urlpatterns = [
    path('difficulties/', DifficultyListView.as_view(), name='difficulty-list'),
]

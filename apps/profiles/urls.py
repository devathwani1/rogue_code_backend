from django.urls import path
from apps.profiles.views.profile import ProfileView

urlpatterns = [
    path('me/', ProfileView.as_view(), name='profile-detail'),
]

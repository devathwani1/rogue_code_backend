from django.urls import path
from apps.profiles.views.profile import ProfileView
from apps.profiles.views.profile_stats import ProfileStatsView
from apps.profiles.views.reset_run import ResetRunView
from apps.profiles.views.leaderboard import LeaderboardView

urlpatterns = [
    path('me/', ProfileView.as_view(), name='profile-detail'),
    path('me/stats/', ProfileStatsView.as_view(), name='profile-stats'),
    path('me/reset-run/', ResetRunView.as_view(), name='profile-reset-run'),
    path('leaderboard/', LeaderboardView.as_view(), name='profiles-leaderboard'),
]

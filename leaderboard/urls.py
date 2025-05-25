from django.urls import path
from .views import DailyLeaderboardView, WeeklyLeaderboardView

urlpatterns = [
    path('daily/', DailyLeaderboardView.as_view(), name='daily-leaderboard'),
    path('weekly/', WeeklyLeaderboardView.as_view(), name='weekly-leaderboard'),
]
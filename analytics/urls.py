"""Analytics URLs."""
from django.urls import path
from .views import (
    OverviewStatsView,
    DailyStatsView,
    WeeklyStatsView,
    ProductivityTrendView,
    CategoryStatsView,
)

urlpatterns = [
    path('overview/', OverviewStatsView.as_view(), name='overview_stats'),
    path('daily/', DailyStatsView.as_view(), name='daily_stats'),
    path('weekly/', WeeklyStatsView.as_view(), name='weekly_stats'),
    path('trends/', ProductivityTrendView.as_view(), name='productivity_trends'),
    path('categories/', CategoryStatsView.as_view(), name='category_stats'),
]

"""User URLs."""
from django.urls import path
from accounts.views import CurrentUserView, ProfileView

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
]

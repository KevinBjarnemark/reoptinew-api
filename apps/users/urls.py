from django.urls import path
from .views import Profile, Profiles


urlpatterns = [
    path('profiles/', Profiles.as_view()),
    path('profile/<int:pk>/', Profile.as_view()),
]

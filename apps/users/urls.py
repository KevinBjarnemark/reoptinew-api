from django.urls import path
from .views import Profile, SignUp


urlpatterns = [
    path('profile/<int:pk>/', Profile.as_view()),
    path('sign-up/', SignUp.as_view(), name='sign-up'),
]

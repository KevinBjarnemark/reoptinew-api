from django.urls import path
from .views import Profile, SignUp, UserProfile
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('profile/<int:pk>/', Profile.as_view()),
    path('profile/', UserProfile.as_view(), name='user_profile'),
    path('signup/', SignUp.as_view(), name='signup'),
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
]

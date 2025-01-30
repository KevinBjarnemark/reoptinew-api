from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    Profile,
    SignUp,
    LogIn,
    LogOut,
    UserProfile,
    DeleteAccount,
    UpdateProfileImage,
)


urlpatterns = [
    path(
        "profile/update-image/",
        UpdateProfileImage.as_view(),
        name="update_profile_image",
    ),
    path("profile/<str:identifier>/", Profile.as_view()),
    path("profile/", UserProfile.as_view(), name="profile"),
    path("signup/", SignUp.as_view(), name="signup"),
    path("login/", LogIn.as_view(), name="login"),
    path("logout/", LogOut.as_view(), name="logout"),
    path("delete-account/", DeleteAccount.as_view(), name="delete_account"),
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
]

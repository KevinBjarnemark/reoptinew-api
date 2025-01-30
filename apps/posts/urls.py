from django.urls import path
from .views import PostAPIView, LikeView


urlpatterns = [
    path("posts/", PostAPIView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostAPIView.as_view(), name="post-detail"),
    path("like/<int:post_id>/", LikeView.as_view(), name="like-create"),
]

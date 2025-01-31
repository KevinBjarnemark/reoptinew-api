from django.urls import path
from .views import PostAPIView, LikeView, DeletePostView


urlpatterns = [
    path(
        "post/delete-post/<int:pk>/",
        DeletePostView.as_view(),
        name="delete-post",
    ),
    path("posts/", PostAPIView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostAPIView.as_view(), name="post-detail"),
    path("like/<int:post_id>/", LikeView.as_view(), name="like-create"),
]

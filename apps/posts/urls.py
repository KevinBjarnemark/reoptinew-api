from django.urls import path
from .views import (
    PostAPIView,
    LikeView,
    DeletePostView,
    RatingView,
    CommentView,
)


urlpatterns = [
    path(
        "post/delete-post/<int:pk>/",
        DeletePostView.as_view(),
        name="delete-post",
    ),
    path("posts/", PostAPIView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostAPIView.as_view(), name="post-detail"),
    path("like/<int:post_id>/", LikeView.as_view(), name="like-create"),
    path("ratings/<int:post_id>/", RatingView.as_view(), name="rating-create"),
    path(
        "comments/<int:post_id>/", CommentView.as_view(), name="comment-create"
    ),
]

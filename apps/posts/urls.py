from django.urls import path
from .views import PostAPIView, SinglePost


urlpatterns = [
    path('posts/', PostAPIView.as_view(), name='post-list-create'),
    path('post/<int:pk>/', SinglePost.as_view()),
]

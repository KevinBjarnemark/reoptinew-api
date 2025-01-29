from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from static.utils.environment import is_development
from django.http import JsonResponse


# pylint: disable=unused-argument
def welcome_message(request):
    """Just a welcome message ^^"""
    return JsonResponse({"message": "Welcome to Reoptinew's API!"})


urlpatterns = [
    path('', welcome_message),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('posts/', include('apps.posts.urls')),
]

if is_development():
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

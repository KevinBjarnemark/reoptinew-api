from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from static.py.utils.environment import is_development

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
]

if is_development():
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

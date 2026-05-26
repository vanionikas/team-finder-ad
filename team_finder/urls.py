from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('projects/', include('projects.urls', namespace='projects')),
    path('', lambda request: redirect('/projects/list')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

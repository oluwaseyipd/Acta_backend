"""
Main URL configuration for Acta.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/', include([
        path('auth/', include('accounts.urls.auth_urls')),
        path('users/', include('accounts.urls.user_urls')),
        path('', include('tasks.urls')),
        path('analytics/', include('analytics.urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

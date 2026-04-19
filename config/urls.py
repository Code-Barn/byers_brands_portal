"""
URL configuration for Byers Brands Web Portal.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.brand.urls')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('investor/', include('apps.investor.urls', namespace='investor')),
    path('polly/', include('apps.polly_client.urls', namespace='polly_client')),
    path('feedback/', include('apps.feedback.urls', namespace='feedback')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar URL
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

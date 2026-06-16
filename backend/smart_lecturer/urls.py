from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),
    path('reviews/', include('apps.reviews.urls', namespace='reviews')),
    path('arq/', include('apps.arq.urls', namespace='arq')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('', include('apps.accounts.urls_root')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

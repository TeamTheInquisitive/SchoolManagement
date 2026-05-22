from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/admin/teachers/', include('apps.teachers.urls')),
    path('api/v1/oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

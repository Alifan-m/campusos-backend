from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/cafeteria/', include('cafeteria.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/events/', include('events.urls')),
    path('api/notices/', include('notices.urls')),
    path('api/map/', include('map.urls')),
]

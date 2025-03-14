
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/telegram/', include('telegram_integration.urls')),
    path('api/ai/', include('ai_summarization.urls')),
]

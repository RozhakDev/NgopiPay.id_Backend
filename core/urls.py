from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root_view(request):
    """View sederhana untuk memastikan API berjalan (Sanity Check)"""
    return JsonResponse({
        "status": "success",
        "message": "Selamat datang di API Nongki.id",
        "version": "v1"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_root_view, name='api-root'),
]
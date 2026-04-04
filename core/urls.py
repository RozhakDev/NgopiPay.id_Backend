from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

def api_root_view(request):
    """View sederhana untuk memastikan API berjalan (Sanity Check)"""
    return JsonResponse({
        "status": "success",
        "message": "Selamat datang di API NgopiPay.id",
        "version": "v1"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', api_root_view, name='api-root'),

    path('api/v1/', include('menus.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('payments.urls')),

    path('api/v1/admin/', include('orders.admin_urls')),
    path('api/v1/admin/reports/', include('reports.urls')),

    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'), # File mentah OpenAPI
    path('api/v1/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # Tampilan Swagger UI
    path('api/v1/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'), # Tampilan ReDoc
]
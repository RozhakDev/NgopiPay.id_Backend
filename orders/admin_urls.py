from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .admin_views import AdminOrderViewSet

router = DefaultRouter()
router.register(r'orders', AdminOrderViewSet, basename='admin-order')

urlpatterns = [
    path('', include(router.urls)),
]
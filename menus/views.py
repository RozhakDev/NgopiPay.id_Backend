from rest_framework import viewsets, permissions
from .models import Menu
from .serializers import MenuSerializer


class StaffWritePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)


class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [StaffWritePermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Menu.objects.all()
        
        return Menu.objects.filter(is_available=True)
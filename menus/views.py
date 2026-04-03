from rest_framework import viewsets, permissions
from .models import Menu
from .serializers import MenuSerializer

class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Menu.objects.all()
        
        return Menu.objects.filter(is_available=True)
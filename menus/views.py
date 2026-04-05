from rest_framework import viewsets, permissions
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Menu
from .serializers import MenuSerializer


class StaffWritePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)


@extend_schema_view(
    list=extend_schema(
        summary="Daftar Katalog Menu",
        description="Menampilkan semua menu yang tersedia untuk pelanggan. Admin akan melihat semua menu termasuk yang tidak tersedia.",
        tags=["Menu"]
    ),
    retrieve=extend_schema(
        summary="Detail Menu",
        description="Melihat informasi mendalam tentang satu menu tertentu berdasarkan ID.",
        tags=["Menu"]
    ),
    create=extend_schema(
        summary="Tambah Menu Baru (Admin)",
        description="Menambahkan menu baru ke katalog. Gunakan format **multipart/form-data** untuk mengunggah gambar.",
        request=MenuSerializer,
        tags=["Menu"]
    ),
    update=extend_schema(
        summary="Ubah Menu (Admin)",
        description="Memperbarui seluruh informasi menu termasuk unggah gambar baru.",
        request=MenuSerializer,
        tags=["Menu"]
    ),
    partial_update=extend_schema(
        summary="Ubah Menu Sebagian (Admin)",
        description="Memperbarui beberapa field menu atau menambah gambar.",
        request=MenuSerializer,
        tags=["Menu"]
    ),
    destroy=extend_schema(
        summary="Hapus Menu (Admin)",
        description="Menghapus menu dari katalog secara permanen. Memerlukan otentikasi staff.",
        tags=["Menu"]
    ),
)
class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer
    permission_classes = [StaffWritePermission]
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Menu.objects.prefetch_related('images').all()
        
        return Menu.objects.filter(is_available=True).prefetch_related('images')
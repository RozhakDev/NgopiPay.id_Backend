import logging
from django.contrib import admin
from .models import Menu, MenuImage

logger = logging.getLogger(__name__)


class MenuImageInline(admin.TabularInline):
    model = MenuImage
    extra = 1
    fields = ('image', 'alt_text', 'sort_order')
    ordering = ('sort_order',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'updated_at')
    list_filter = ('is_available',)
    search_fields = ('name',)
    list_editable = ('is_available', 'price')
    inlines = [MenuImageInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        logger.info(
            "Menu disimpan melalui Django Admin. user=%s, id=%s, nama=%s, aksi=%s",
            request.user,
            obj.id,
            obj.name,
            "ubah" if change else "baru",
        )

    def delete_model(self, request, obj):
        logger.info(
            "Menu dihapus melalui Django Admin. user=%s, id=%s, nama=%s",
            request.user,
            obj.id,
            obj.name,
        )
        super().delete_model(request, obj)
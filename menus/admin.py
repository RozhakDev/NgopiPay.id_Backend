from django.contrib import admin
from .models import Menu, MenuImage


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
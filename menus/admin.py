from django.contrib import admin
from .models import Menu

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'updated_at')
    list_filter = ('is_available',)
    search_fields = ('name',)
    list_editable = ('is_available', 'price')
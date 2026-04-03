from rest_framework import serializers
from .models import Menu

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'price', 'description', 'image_url', 'is_available', 'updated_at']
        read_only_fields = ['id', 'updated_at']
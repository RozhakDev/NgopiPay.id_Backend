from rest_framework import serializers
from django.db import transaction
from .models import Menu, MenuImage


class MenuImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MenuImage
        fields = ['id', 'image_url', 'alt_text', 'sort_order', 'created_at']
        read_only_fields = ['id', 'image_url', 'created_at']

    def get_image_url(self, obj):
        if not obj.image:
            return None

        request = self.context.get('request')
        image_url = obj.image.url
        return request.build_absolute_uri(image_url) if request else image_url

class MenuSerializer(serializers.ModelSerializer):
    images = MenuImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        allow_empty=False,
    )
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            'id',
            'name',
            'price',
            'description',
            'image_url',
            'primary_image_url',
            'images',
            'uploaded_images',
            'is_available',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at', 'primary_image_url', 'images']

    def get_primary_image_url(self, obj):
        primary_image_url = obj.primary_image_url
        if not primary_image_url:
            return None

        request = self.context.get('request')
        return request.build_absolute_uri(primary_image_url) if request else primary_image_url

    @staticmethod
    def _create_menu_images(menu, uploaded_images):
        for index, image_file in enumerate(uploaded_images):
            MenuImage.objects.create(
                menu=menu,
                image=image_file,
                sort_order=index,
            )

    @transaction.atomic
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        menu = super().create(validated_data)
        if uploaded_images:
            self._create_menu_images(menu, uploaded_images)
        return menu

    @transaction.atomic
    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        menu = super().update(instance, validated_data)
        if uploaded_images:
            start_order = menu.images.count()
            for offset, image_file in enumerate(uploaded_images, start=start_order):
                MenuImage.objects.create(
                    menu=menu,
                    image=image_file,
                    sort_order=offset,
                )
        return menu
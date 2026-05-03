# apps/vault/serializers.py
from rest_framework import serializers
from .models import VaultItem

class VaultItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaultItem
        fields = [
            'id', 'title', 'description', 'item_type', 'original_filename',
            'file_size', 'mime_type', 'uploaded_at', 'tags'
        ]
        read_only_fields = ['id', 'file_size', 'mime_type', 'uploaded_at']

class VaultUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    item_type = serializers.ChoiceField(choices=VaultItem._meta.get_field('item_type').choices)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
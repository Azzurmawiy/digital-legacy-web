# apps/vault/views.py
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse
import uuid
import mimetypes
from .models import VaultItem
from .serializers import VaultItemSerializer, VaultUploadSerializer
from .encryption import (
    generate_data_key, encrypt_file_content, 
    encrypt_data_key, decrypt_data_key, decrypt_file_content
)
class VaultListView(generics.ListAPIView):
    serializer_class = VaultItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VaultItem.objects.filter(user=self.request.user)

class VaultUploadView(generics.CreateAPIView):
    serializer_class = VaultUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        file_obj = serializer.validated_data['file']
        user = self.request.user

        # Read file content
        file_content = file_obj.read()
        original_filename = file_obj.name
        mime_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        file_size = len(file_content)

        # Generate per-file data key + encrypt content
        data_key = generate_data_key()
        encrypted_content = encrypt_file_content(file_content, data_key)

        # Encrypt the data key with master key
        encrypted_data_key = encrypt_data_key(data_key)

        # Generate unique S3 key
        s3_key = f"vault/{user.id}/{uuid.uuid4()}/{original_filename}"

        # Upload encrypted file to storage
        default_storage.save(s3_key, ContentFile(encrypted_content))

        # Save metadata
        vault_item = VaultItem.objects.create(
            user=user,
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            item_type=serializer.validated_data['item_type'],
            s3_key=s3_key,
            encrypted_data_key=encrypted_data_key,
            file_size=file_size,
            mime_type=mime_type,
            original_filename=original_filename,
            tags=serializer.validated_data.get('tags', [])
        )

        return vault_item

class VaultDownloadView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VaultItem.objects.all()
    serializer_class = VaultItemSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            vault_item = VaultItem.objects.get(id=kwargs['pk'], user=request.user)
        except VaultItem.DoesNotExist:
            raise NotFound(detail="Vault item not found.")
        
        try:
            # Get encrypted file from S3
            encrypted_content = default_storage.open(vault_item.s3_key).read()
            
            # Decrypt data key then decrypt file
            data_key = decrypt_data_key(vault_item.encrypted_data_key)
            decrypted_content = decrypt_file_content(encrypted_content, data_key)

            # Return as downloadable response
            response = FileResponse(ContentFile(decrypted_content), content_type=vault_item.mime_type)
            response['Content-Disposition'] = f'attachment; filename="{vault_item.original_filename}"'
            return response
        except Exception as e:
            return Response(
                {"error": "Failed to decrypt and retrieve file."},
                status=status.HTTP_400_BAD_REQUEST
            )

class VaultDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VaultItem.objects.all()
    serializer_class = VaultItemSerializer

    def get_queryset(self):
        return VaultItem.objects.filter(user=self.request.user)
    
    def perform_destroy(self, instance):
        # Delete file from storage as well
        try:
            default_storage.delete(instance.s3_key)
        except Exception:
            pass
        instance.delete()

class VaultUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VaultItem.objects.all()
    serializer_class = VaultItemSerializer

    def get_queryset(self):
        return VaultItem.objects.filter(user=self.request.user)
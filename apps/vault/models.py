from django.db import models
import uuid
from apps.authentication.models import User
from django.utils import timezone
# Create your models here.
# apps/vault/models.py


class VaultItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vault_items')
    
    # Metadata
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=50, choices=[
        ('document', 'Document'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('voice', 'Voice Note'),
        ('memory', 'Memory'),
        ('note', 'Secure Note'),
        ('message', 'Heir Message'),
    ])
    
    # Storage
    s3_key = models.CharField(max_length=500)           # Path in S3
    encrypted_data_key = models.TextField()             # Encrypted per-item data key (envelope encryption)
    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)
    original_filename = models.CharField(max_length=255)
    
    # Security & Audit
    is_encrypted = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'uploaded_at']),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.user.email})"
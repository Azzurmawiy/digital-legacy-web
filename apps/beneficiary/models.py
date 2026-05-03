import uuid
from django.db import models
from django.conf import settings


class Beneficiary(models.Model):
    """
    Beneficiary details designated by a user to receive digital legacy assets.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='beneficiaries'
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    relationship = models.CharField(max_length=100)
    
    # Permissions stored as JSON (e.g., {"can_view_vault": True, "can_view_memories": False})
    permissions = models.JSONField(default=dict)
    
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'beneficiaries'
        verbose_name = 'Beneficiary'
        verbose_name_plural = 'Beneficiaries'
        unique_together = ('user', 'email')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.email}) - Beneficiary of {self.user.email}"

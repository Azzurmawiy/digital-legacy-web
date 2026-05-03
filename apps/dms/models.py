import uuid
from django.db import models
from django.conf import settings


class DMSConfig(models.Model):
    """
    Dead Man's Switch Configuration.
    Stores user preferences for inactivity threshold and cooling-off period.
    """

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        WARNING_1 = 'WARNING_1', 'Warning 1 (75%)'
        WARNING_2 = 'WARNING_2', 'Warning 2 (90%)'
        COOLING_OFF = 'COOLING_OFF', 'Cooling Off'
        RELEASED = 'RELEASED', 'Released'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dms_config'
    )
    inactivity_threshold_days = models.PositiveIntegerField(default=90)
    cooling_off_days = models.PositiveIntegerField(default=7)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    last_triggered = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dms_config'
        verbose_name = 'DMS Configuration'
        verbose_name_plural = 'DMS Configurations'

    def __str__(self):
        return f"DMS Config for {self.user.email}"


class Heartbeat(models.Model):
    """
    Immutable log of user activity signals from web or mobile.
    Used as proof of life.
    """

    class Source(models.TextChoices):
        WEB = 'WEB', 'Web'
        MOBILE = 'MOBILE', 'Mobile'
        API = 'API', 'API'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='heartbeats'
    )
    source = models.CharField(max_length=20, choices=Source.choices)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_hash = models.CharField(max_length=64)  # SHA-256 hash of IP

    class Meta:
        db_table = 'heartbeats'
        verbose_name = 'Heartbeat'
        verbose_name_plural = 'Heartbeats'
        ordering = ['-timestamp']

    def __str__(self):
        return f"Heartbeat from {self.user.email} at {self.timestamp}"

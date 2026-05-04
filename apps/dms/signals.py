from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import DMSConfig

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_default_dms_config(sender, instance, created, **kwargs):
    """
    Automatically create a default DMS configuration for every new user.
    """
    if created:
        DMSConfig.objects.get_or_create(
            user=instance,
            defaults={
                'inactivity_threshold_days': 90,
                'status': DMSConfig.Status.ACTIVE
            }
        )

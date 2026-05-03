from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.dms.models import DMSConfig
from apps.dms.release import release_assets_to_beneficiaries
from django.contrib.auth import get_user_model
from apps.notifications.tasks import send_email_notification, send_sms_notification

User = get_user_model()


@shared_task
def check_dms_inactivity():
    """
    Daily cron job to check all active DMS configurations and trigger alerts or
    transitions based on inactivity_threshold_days.
    """
    configs = DMSConfig.objects.filter(status__in=[
        DMSConfig.Status.ACTIVE,
        DMSConfig.Status.WARNING_1,
        DMSConfig.Status.WARNING_2,
        DMSConfig.Status.COOLING_OFF
    ]).select_related('user')

    now = timezone.now()

    for config in configs:
        user = config.user
        last_active = user.last_active_at
        days_inactive = (now - last_active).days

        # Cooling off handling
        if config.status == DMSConfig.Status.COOLING_OFF:
            cooling_days_elapsed = (now - config.last_triggered).days if config.last_triggered else 0
            
            # Send notifications during cooling off
            if cooling_days_elapsed == 3:
                send_email_notification.delay(
                    user.id,
                    "URGENT: Digital Legacy Cooling-Off Period (Day 3)",
                    f"Your account has been inactive. Your digital assets will be released in {config.cooling_off_days - 3} days. Log in to cancel."
                )
            elif cooling_days_elapsed == 7:
                send_email_notification.delay(
                    user.id,
                    "FINAL WARNING: Digital Legacy Release Imminent",
                    f"Your account has been inactive. Your digital assets will be released today. Log in immediately to cancel."
                )

            # If cooling off period is over, release assets
            if cooling_days_elapsed >= config.cooling_off_days:
                config.status = DMSConfig.Status.RELEASED
                config.save(update_fields=['status'])
                release_assets_to_beneficiaries.delay(user.id)
            
            continue

        # Normal inactivity check
        threshold = config.inactivity_threshold_days
        
        # 100% threshold -> trigger cooling off
        if days_inactive >= threshold and config.status != DMSConfig.Status.COOLING_OFF:
            config.status = DMSConfig.Status.COOLING_OFF
            config.last_triggered = now
            config.save(update_fields=['status', 'last_triggered'])
            
            send_email_notification.delay(
                user.id,
                "ACTION REQUIRED: Digital Legacy Cooling-Off Period Started",
                f"You have been inactive for {threshold} days. A {config.cooling_off_days}-day cooling-off period has started. Log in to cancel the release of your assets."
            )
            send_sms_notification.delay(
                user.id,
                f"Digital Legacy: Cooling-off started. Log in within {config.cooling_off_days} days to prevent asset release."
            )
            continue

        # 90% threshold -> warning 2
        warning_2_threshold = int(threshold * 0.90)
        if days_inactive >= warning_2_threshold and config.status not in [DMSConfig.Status.WARNING_2, DMSConfig.Status.COOLING_OFF]:
            config.status = DMSConfig.Status.WARNING_2
            config.save(update_fields=['status'])
            
            send_email_notification.delay(
                user.id,
                "URGENT: Digital Legacy Inactivity Warning (90%)",
                f"You have been inactive for {days_inactive} days. Please log in soon to reset your inactivity timer and prevent your assets from entering the cooling-off period."
            )
            send_sms_notification.delay(
                user.id,
                f"Digital Legacy Warning: You have been inactive for {days_inactive} days. Log in soon to reset."
            )
            continue

        # 75% threshold -> warning 1
        warning_1_threshold = int(threshold * 0.75)
        if days_inactive >= warning_1_threshold and config.status == DMSConfig.Status.ACTIVE:
            config.status = DMSConfig.Status.WARNING_1
            config.save(update_fields=['status'])
            
            send_email_notification.delay(
                user.id,
                "Notice: Digital Legacy Inactivity Warning",
                f"You have been inactive for {days_inactive} days. Just a reminder to log in to keep your account active."
            )
            continue

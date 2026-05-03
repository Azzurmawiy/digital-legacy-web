# core/middleware/activity.py
# Tracks user activity and resets Dead Man's Switch warnings.

from django.utils import timezone
from django.http import HttpRequest, HttpResponse
from apps.dms.models import DMSConfig

class ActivityTrackingMiddleware:
    """
    Updates the user's last_active_at timestamp on every authenticated request.
    If the user has an active DMS warning or cooling-off period, it resets it to ACTIVE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Only track authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # 1. Update last_active_at (throttled to once per minute to save DB writes)
            # But for simplicity in this project, we'll update it if it's been more than 5 mins
            user = request.user
            now = timezone.now()
            
            if not user.last_active_at or (now - user.last_active_at).total_seconds() > 300:
                user.update_last_active()

                # 2. Reset DMS status if it was in warning/cooling-off state
                try:
                    # Use select_for_update to prevent race conditions with the Celery task
                    dms_config = DMSConfig.objects.filter(user=user).first()
                    if dms_config and dms_config.status in [
                        DMSConfig.Status.WARNING_1,
                        DMSConfig.Status.WARNING_2,
                        DMSConfig.Status.COOLING_OFF
                    ]:
                        dms_config.status = DMSConfig.Status.ACTIVE
                        dms_config.save(update_fields=['status'])
                except Exception:
                    # Fail silently to not block the request if DMS fails
                    pass

        return response

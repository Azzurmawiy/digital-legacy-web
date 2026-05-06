from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification

@shared_task
def send_email_notification(user_id, subject, message, recipient_email=None):
    """
    Async task to send an email notification and log it.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return
        
    target_email = recipient_email or user.email
    
    notification = Notification.objects.create(
        user=user,
        channel=Notification.Channel.EMAIL,
        subject=subject,
        message=message
    )
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
        notification.status = Notification.Status.SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=['status', 'sent_at'])
    except Exception as e:
        notification.status = Notification.Status.FAILED
        notification.error_message = str(e)
        notification.save(update_fields=['status', 'error_message'])

@shared_task
def send_sms_notification(user_id, message):
    """
    Async task to send an SMS notification via Twilio and log it.
    """
    from django.contrib.auth import get_user_model
    from twilio.rest import Client
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return
        
    notification = Notification.objects.create(
        user=user,
        channel=Notification.Channel.SMS,
        message=message
    )
    
    if user.phone and settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=user.phone
            )
            
            notification.status = Notification.Status.SENT
            notification.sent_at = timezone.now()
            notification.save(update_fields=['status', 'sent_at'])
        except Exception as e:
            notification.status = Notification.Status.FAILED
            notification.error_message = str(e)
            notification.save(update_fields=['status', 'error_message'])
    else:
        notification.status = Notification.Status.FAILED
        notification.error_message = "Phone number missing or Twilio not configured."
        notification.save(update_fields=['status', 'error_message'])

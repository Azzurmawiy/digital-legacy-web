import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def send_test_email(recipient):
    print(f"Attempting to send test email to: {recipient}...")
    print(f"Using Backend: {settings.EMAIL_BACKEND}")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    print(f"TLS: {settings.EMAIL_USE_TLS}")
    print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    try:
        send_mail(
            subject='Digital Legacy - Real Email Test',
            message='Congratulations! Your Digital Legacy platform is now sending real emails.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("\nSUCCESS: Email sent! Please check your inbox (and spam folder).")
    except Exception as e:
        print(f"\nFAILED: Could not send email.")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_email.py your-email@example.com")
    else:
        send_test_email(sys.argv[1])

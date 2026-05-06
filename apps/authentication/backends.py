from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class PhoneOrEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using either
    their email address or their phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Check for user by email OR phone
            user = User.objects.get(Q(email__iexact=username) | Q(phone=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # This should ideally not happen if phone is unique
            return User.objects.filter(Q(email__iexact=username) | Q(phone=username)).first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

# core/utils/validators.py
# Custom validators for password strength and phone numbers.

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    """
    Enforces strong password policy:
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    Minimum length is enforced separately by Django's MinimumLengthValidator.
    """

    def validate(self, password: str, user=None) -> None:
        errors = []

        if not re.search(r'[A-Z]', password):
            errors.append(_('Password must contain at least one uppercase letter.'))

        if not re.search(r'[a-z]', password):
            errors.append(_('Password must contain at least one lowercase letter.'))

        if not re.search(r'\d', password):
            errors.append(_('Password must contain at least one digit.'))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
            errors.append(_('Password must contain at least one special character.'))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self) -> str:
        return _(
            'Your password must contain at least one uppercase letter, '
            'one lowercase letter, one digit, and one special character.'
        )

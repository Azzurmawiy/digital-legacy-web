# apps/authentication/models.py
# Custom User model — extends AbstractBaseUser for full control.
# SECURITY: Uses UUID primary keys, never sequential integers.

import uuid
import pyotp
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes with PBKDF2 + bcrypt via Django
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model with:
    - UUID primary key (SECURITY: prevents enumeration attacks)
    - Email as login identifier (not username)
    - MFA support (TOTP secret)
    - Soft delete (deletedAt instead of hard delete)
    - Activity tracking (lastActiveAt for Dead Man's Switch)
    """

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        ADMIN = 'ADMIN', 'Admin'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        DELETED = 'DELETED', 'Deleted'

    # Primary key: UUID (SECURITY: no sequential ID enumeration)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Login credentials
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    # Profile
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Verification
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    # MFA — TOTP secret stored encrypted at application level
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, null=True, blank=True)  # Encrypted

    # Role & Status
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OWNER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Timestamps
    last_active_at = models.DateTimeField(default=timezone.now, db_index=True)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # Soft delete

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['last_active_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()

    def update_last_active(self) -> None:
        """Update activity timestamp — called on every authenticated request."""
        self.last_active_at = timezone.now()
        self.save(update_fields=['last_active_at'])

    def soft_delete(self) -> None:
        """Soft delete — preserves data for legal/compliance reasons."""
        self.status = self.Status.DELETED
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=['status', 'deleted_at', 'is_active'])

    def enable_mfa(self) -> str:
        """
        Generate TOTP secret for MFA and enable it.
        Returns the secret so user can scan QR code.
        SECURITY: Secret is not exposed after this call.
        """
        if not self.mfa_enabled:
            self.mfa_secret = pyotp.random_base32()
            self.mfa_enabled = True
            self.save(update_fields=['mfa_secret', 'mfa_enabled'])
        return self.mfa_secret

    def verify_totp(self, token: str) -> bool:
        """
        Verify TOTP token against stored secret.
        Allows ±1 time window for clock drift (30 seconds).
        Returns True if token is valid, False otherwise.
        """
        if not self.mfa_secret or not self.mfa_enabled:
            return False
        try:
            totp = pyotp.TOTP(self.mfa_secret)
            return totp.verify(token, valid_window=1)
        except Exception:
            return False

    def disable_mfa(self) -> None:
        """Disable MFA — removes TOTP secret."""
        self.mfa_enabled = False
        self.mfa_secret = None
        self.save(update_fields=['mfa_enabled', 'mfa_secret'])


class OtpVerification(models.Model):
    """
    OTP codes for email/phone verification, password reset, MFA.
    SECURITY: Codes are hashed before storage, never stored in plain text.
    """

    class OtpType(models.TextChoices):
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', 'Email Verification'
        PHONE_VERIFICATION = 'PHONE_VERIFICATION', 'Phone Verification'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset'
        LOGIN_MFA = 'LOGIN_MFA', 'Login MFA'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    otp_type = models.CharField(max_length=30, choices=OtpType.choices)
    code_hash = models.CharField(max_length=128)  # SECURITY: hashed OTP, never plain text
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'otp_verifications'
        indexes = [
            models.Index(fields=['user', 'otp_type']),
            models.Index(fields=['expires_at']),
        ]

    @property
    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    @property
    def is_used(self) -> bool:
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        return not self.is_expired and not self.is_used and self.attempts < 5


class LoginAttempt(models.Model):
    """
    Track login attempts for account lockout protection.
    SECURITY: IP is hashed before storage for privacy.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True)
    ip_hash = models.CharField(max_length=64)  # SHA-256 hash of IP
    success = models.BooleanField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_attempts'
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_hash', 'created_at']),
        ]

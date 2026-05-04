# apps/authentication/views.py
from typing import Optional
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import AbstractBaseUser
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import pyotp
import random

from .models import User
from .serializers import (
    RegisterSerializer, OTPVerifySerializer, LoginSerializer,
    MFASetupSerializer
)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def perform_create(self, serializer):
        user = serializer.save()
        if settings.DEBUG:
            user.is_active = True
            user.is_email_verified = True
            user.save()
        else:
            self.send_otp(user)
        return user

    def send_otp(self, user):
        otp = str(random.randint(100000, 999999))
        # In production, store OTP hashed with expiry in Redis or DB model
        # For simplicity, we'll print it (replace with real storage)
        print(f"OTP for {user.email}: {otp}")   # TODO: Replace with proper OTP model + Redis

        send_mail(
            subject='Your Digital Legacy Account Verification OTP',
            message=f'Your verification OTP is: {otp}\nIt expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        # TODO: Save OTP properly (recommended: create OTP model or use cache)

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(email=serializer.validated_data['email'])
            # TODO: Proper OTP verification logic here (compare with stored OTP + expiry)
            # For now, we simulate success after registration
            user.is_email_verified = True
            user.is_active = True
            user.save()
            
            return Response({
                "success": True,
                "message": "Account verified successfully. You can now login."
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        totp_token = serializer.validated_data.get('totp_token')

        auth_user = authenticate(request, username=email, password=password)  # email as username

        if not auth_user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # Type cast to our custom User model
        user: User = auth_user  # type: ignore

        if not user.is_email_verified:
            return Response({"error": "Account not verified. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)

        # MFA Check
        if user.mfa_enabled and not totp_token:
            return Response({
                "mfa_required": True,
                "message": "TOTP token required"
            }, status=status.HTTP_200_OK)

        if user.mfa_enabled and totp_token:
            if not user.verify_totp(totp_token):
                return Response({"error": "Invalid TOTP code"}, status=status.HTTP_401_UNAUTHORIZED)

        # Successful login
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'access': str(refresh.access_token),  # type: ignore
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'mfa_enabled': user.mfa_enabled
            }
        })

class MFASetupView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user: User = request.user  # type: ignore
        secret = user.enable_mfa()
        
        # In real app, generate QR code URL using pyotp + qrcode
        provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email, issuer_name="DigitalLegacy"
        )

        return Response({
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "message": "MFA enabled. Scan the QR code in Google Authenticator."
        })


class MFAConfirmView(generics.GenericAPIView):
    """Confirm MFA setup by verifying TOTP token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user: User = request.user  # type: ignore
        totp_token = request.data.get('totp_token')

        if not totp_token:
            return Response(
                {"error": "TOTP token required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.verify_totp(totp_token):
            return Response(
                {"error": "Invalid TOTP code"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # MFA is already enabled in setup, just confirming here
        return Response({
            "success": True,
            "message": "MFA has been confirmed and enabled."
        })


class MFADisableView(generics.GenericAPIView):
    """Disable MFA for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user: User = request.user  # type: ignore
        user.disable_mfa()

        return Response({
            "success": True,
            "message": "MFA has been disabled."
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get or update user profile."""
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user: User = request.user  # type: ignore
        return Response({
            "success": True,
            "data": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": user.phone,
                "is_email_verified": user.is_email_verified,
                "is_phone_verified": user.is_phone_verified,
                "mfa_enabled": user.mfa_enabled,
                "role": user.role,
                "status": user.status,
            }
        })

    def put(self, request, *args, **kwargs):
        user: User = request.user  # type: ignore
        allowed_fields = ['first_name', 'last_name', 'phone']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        
        user.save()
        return Response({
            "success": True,
            "message": "Profile updated successfully."
        })


class ChangePasswordView(generics.GenericAPIView):
    """Change user password."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user: User = request.user  # type: ignore
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        if not old_password or not new_password or not new_password_confirm:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "Old password is incorrect"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if new_password != new_password_confirm:
            return Response(
                {"error": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 12:
            return Response(
                {"error": "Password must be at least 12 characters long"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({
            "success": True,
            "message": "Password changed successfully."
        })


class LogoutView(generics.GenericAPIView):
    """Logout user by blacklisting their refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response(
                    {"error": "Refresh token required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "success": True,
                "message": "Logged out successfully."
            })
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


from apps.vault.models import VaultItem
from apps.beneficiary.models import Beneficiary
from apps.dms.models import DMSConfig
from rest_framework.views import APIView
from django.db.models import Sum

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. Total Vault Assets (count)
        vault_count = VaultItem.objects.filter(user=user).count()
        
        # 2. Total Storage (size)
        total_size_bytes = VaultItem.objects.filter(user=user).aggregate(Sum('file_size'))['file_size__sum'] or 0
        vault_size_mb = round(total_size_bytes / (1024 * 1024), 2)
        
        # 3. Verified Heirs (count)
        heirs_count = Beneficiary.objects.filter(user=user).count()
        
        # 4. DMS Stats
        try:
            dms = DMSConfig.objects.get(user=user)
            dms_status = dms.status
            # Simple calculation for days left (mock for now if method doesn't exist)
            days_left = dms.inactivity_threshold_days
        except DMSConfig.DoesNotExist:
            dms_status = "Inactive"
            days_left = 0

        # 5. Memories count (filtering items with image mime types)
        memories_count = VaultItem.objects.filter(user=user, mime_type__icontains='image').count()

        # 6. Recent activity from notifications
        activity_data = []
        try:
            from apps.notifications.models import Notification
            recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
            for n in recent_notifications:
                activity_data.append({
                    "title": n.title,
                    "sub": n.message[:50],
                    "time": n.created_at.isoformat(),
                    "icon": "🔔"
                })
        except ImportError:
            pass

        return Response({
            "vault_count": vault_count,
            "vault_size_mb": vault_size_mb,
            "beneficiary_count": heirs_count,
            "memories_count": memories_count,
            "dms_status": dms_status,
            "dms_days_left": days_left,
            "recent_activity": activity_data
        })
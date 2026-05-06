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
        # Always trigger OTP verification to allow testing live email authentication
        self.send_otp(user)
        return user

    def send_otp(self, user):
        otp = str(random.randint(100000, 999999))
        
        # 1. Send via Email
        from apps.notifications.tasks import send_email_notification
        send_email_notification.delay(
            user.id,
            subject='Your Digital Legacy Account Verification OTP',
            message=f'Your verification OTP is: {otp}\nIt expires in 10 minutes.'
        )
        
        # 2. Send via SMS if phone is available
        if user.phone:
            from apps.notifications.tasks import send_sms_notification
            send_sms_notification.delay(
                user.id,
                message=f"Your Digital Legacy verification code is: {otp}"
            )
        
        print(f"OTP for {user.email}: {otp}")

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

class ResendOTPView(generics.GenericAPIView):
    """Allows users to request a new OTP if they didn't receive the previous one."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                return Response({"message": "Account already verified."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Re-use the logic from RegisterView
            view = RegisterView()
            view.send_otp(user)
            
            return Response({
                "success": True, 
                "message": "Verification code resent successfully."
            })
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        totp_token = serializer.validated_data.get('totp_token')

        auth_user = authenticate(request, username=username, password=password)

        if not auth_user:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        user: User = auth_user  # type: ignore

        # MFA Check (TOTP)
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
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'mfa_enabled': user.mfa_enabled
            }
        })

    def send_login_otp(self, user, otp_type=None):
        from .models import OtpVerification
        from django.utils import timezone
        from datetime import timedelta
        
        otp_type = otp_type or OtpVerification.OtpType.LOGIN_MFA
        otp = str(random.randint(100000, 999999))
        
        # Save to DB
        OtpVerification.objects.create(
            user=user,
            otp_type=otp_type,
            code_hash=otp, # SECURITY: In production, hash this!
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        from apps.notifications.tasks import send_email_notification
        send_email_notification.delay(
            user.id,
            subject='Secure Login Code',
            message=f'Your verification code is: {otp}\nIt expires in 10 minutes.'
        )
        print(f"LOGIN OTP for {user.email}: {otp}")

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
        dms_threshold = 90  # Default
        safety_score = 100
        try:
            dms = DMSConfig.objects.get(user=user)
            # Normalize status for frontend (Active vs ACTIVE)
            dms_status = "Active" if dms.status == "ACTIVE" else dms.status
            dms_threshold = dms.inactivity_threshold_days
            
            # Calculate actual days left based on user's last activity
            delta = timezone.now() - user.last_active_at
            days_left = max(0, dms_threshold - delta.days)
            
            # Calculate safety score (percentage of time remaining)
            if dms_threshold > 0:
                safety_score = round((days_left / dms_threshold) * 100)
        except DMSConfig.DoesNotExist:
            dms_status = "Inactive"
            days_left = 0
            safety_score = 0

        # 5. Memories count (filtering items with image mime types)
        memories_count = VaultItem.objects.filter(user=user, mime_type__icontains='image').count()

        # 6. Recent activity from notifications
        activity_data = []
        try:
            from apps.notifications.models import Notification
            recent_notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
            for n in recent_notifications:
                activity_data.append({
                    "title": n.subject or "System Notification",
                    "sub": n.message[:50],
                    "time": n.created_at.isoformat(),
                    "icon": "🔔"
                })
        except (ImportError, AttributeError):
            pass

        # 7. Recent Vault Assets
        recent_vault = VaultItem.objects.filter(user=user).order_by('-uploaded_at')[:3]
        recent_vault_data = [{
            "id": str(item.id),
            "title": item.title,
            "type": item.item_type,
            "uploaded_at": item.uploaded_at.isoformat()
        } for item in recent_vault]

        return Response({
            "vault_count": vault_count,
            "vault_size_mb": vault_size_mb,
            "beneficiary_count": heirs_count,
            "memories_count": memories_count,
            "dms_status": dms_status,
            "dms_days_left": days_left,
            "dms_threshold": dms_threshold,
            "safety_score": safety_score,
            "recent_activity": activity_data,
            "recent_vault": recent_vault_data
        })
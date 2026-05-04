# apps/authentication/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyOTPView,
    LoginView,
    MFASetupView,
    MFAConfirmView,
    MFADisableView,
    UserProfileView,
    ChangePasswordView,
    LogoutView,
    DashboardStatsView,
)

app_name = 'auth'

urlpatterns = [
    # Registration & Verification
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('stats/', DashboardStatsView.as_view(), name='stats'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # MFA Management
    path('mfa/setup/', MFASetupView.as_view(), name='mfa-setup'),
    path('mfa/confirm/', MFAConfirmView.as_view(), name='mfa-confirm'),
    path('mfa/disable/', MFADisableView.as_view(), name='mfa-disable'),
]

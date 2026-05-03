# config/urls.py
# Root URL configuration — all routes registered here.
# API versioned under /api/v1/

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from core.views import HealthCheckView
from core.exceptions.handlers import api_404_handler, api_500_handler

urlpatterns = [
    # ---- Root redirect ----
    path('', RedirectView.as_view(url='health/', permanent=False), name='root'),

    # ---- Health Check (no auth) ----
    path('health/', HealthCheckView.as_view(), name='health-check'),

    # ---- Admin (restrict in production via ALLOWED_HOSTS + IP whitelist) ----
    path('django-admin/', admin.site.urls),

    # ---- API v1 ----
    path('api/v1/', include([
        path('health/', HealthCheckView.as_view(), name='health-check-v1'),

        # Auth endpoints (Sprint 2)
        path('auth/', include('apps.authentication.urls', namespace='auth')),

        # Vault endpoints (Sprint 3)
        path('vault/', include('apps.vault.urls', namespace='vault')),

        # Dead Man's Switch (Sprint 4)
        path('dms/', include('apps.dms.urls', namespace='dms')),

        # Beneficiary management (Sprint 5)
        path('beneficiaries/', include('apps.beneficiary.urls', namespace='beneficiary')),

        # Notifications (Sprint 6)
        path('notifications/', include('apps.notifications.urls', namespace='notifications')),

        # Audit logs (Admin only)
        path('audit/', include('apps.audit.urls', namespace='audit')),
    ])),
]

# ---- API Documentation (dev only) ----
if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

# ---- Custom error handlers ----
handler404 = 'core.exceptions.handlers.api_404_handler'
handler500 = 'core.exceptions.handlers.api_500_handler'

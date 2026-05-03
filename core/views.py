# core/views.py
# Health check view — used by load balancers and CI smoke tests.

from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle


class HealthCheckView(APIView):
    """
    GET /health/
    Returns system health status. No authentication required.
    Used by:
    - Kubernetes liveness + readiness probes
    - CI/CD smoke tests post-deployment
    - Load balancer health checks
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [AnonRateThrottle]

    def get(self, request):
        return Response({
            'success': True,
            'data': {
                'status': 'ok',
                'service': 'digital-legacy-api',
                'version': 'v1',
                'environment': settings.DEBUG and 'development' or 'production',
                'timestamp': timezone.now().isoformat(),
            },
        })

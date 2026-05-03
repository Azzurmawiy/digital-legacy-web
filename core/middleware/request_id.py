# core/middleware/request_id.py
# Injects a unique X-Request-Id into every request and response.
# Used for end-to-end request tracing across logs.

import uuid
import logging
import time
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger('core')


class RequestIdMiddleware:
    """Attach a unique request ID to every request for traceability."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = request.headers.get('X-Request-Id') or str(uuid.uuid4())
        request.request_id = request_id  # Attach to request object

        start_time = time.monotonic()
        response = self.get_response(request)

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        response['X-Request-Id'] = request_id

        # Structured request log — SECURITY: never log Authorization or body
        logger.info(
            'HTTP request',
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'user_agent': request.headers.get('User-Agent', ''),
                # Partial IP for privacy
                'ip': self._mask_ip(request.META.get('REMOTE_ADDR', '')),
            },
        )

        return response

    @staticmethod
    def _mask_ip(ip: str) -> str:
        """Mask last octet of IPv4 for privacy compliance."""
        parts = ip.split('.')
        if len(parts) == 4:
            return f'{parts[0]}.{parts[1]}.{parts[2]}.xxx'
        return 'masked'

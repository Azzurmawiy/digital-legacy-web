# core/middleware/audit.py
# Records all mutating API requests to the immutable audit log.
# READ requests (GET) are logged at DEBUG level only.

import hashlib
import logging
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger('core')

# Methods that modify state — always audited
MUTATING_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


class AuditMiddleware:
    """
    Audit trail middleware:
    - Logs all POST/PUT/PATCH/DELETE requests after they complete
    - Records actor (user), path, method, status, request ID
    - SECURITY: Never logs request body (may contain passwords/keys)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        if request.method in MUTATING_METHODS and request.path.startswith('/api/'):
            self._log_audit(request, response)

        return response

    def _log_audit(self, request: HttpRequest, response: HttpResponse) -> None:
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = str(request.user.id)

        ip = request.META.get('REMOTE_ADDR', '')
        ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16] if ip else None

        logger.info(
            'API audit',
            extra={
                'request_id': getattr(request, 'request_id', None),
                'actor_id': user_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'result': 'SUCCESS' if response.status_code < 400 else 'FAILURE',
                'ip_hash': ip_hash,
                'user_agent': request.headers.get('User-Agent', '')[:200],
            },
        )

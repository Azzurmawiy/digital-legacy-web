# core/middleware/security_headers.py
# Adds extra security headers beyond what Django's SecurityMiddleware provides.

from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """
    Adds hardened security headers to every response.
    Works alongside Django's built-in SecurityMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        # Prevent MIME sniffing (already set by Django but being explicit)
        response['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking (already set but being explicit)
        response['X-Frame-Options'] = 'DENY'

        # Permissions Policy — restrict browser features
        response['Permissions-Policy'] = (
            'geolocation=(), camera=(), microphone=(), '
            'payment=(), usb=(), magnetometer=()'
        )

        # Remove server identification header (security through obscurity)
        if 'Server' in response:
            del response['Server']
        if 'X-Powered-By' in response:
            del response['X-Powered-By']

        # Cache control for API responses — never cache auth/sensitive data
        if request.path.startswith('/api/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
            response['Pragma'] = 'no-cache'

        return response

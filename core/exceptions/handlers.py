# core/exceptions/handlers.py
# Custom DRF exception handler — ensures ALL errors return our standard
# {success, error: {message, code}} envelope.

import json
import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, JsonResponse
from rest_framework import status
from rest_framework.exceptions import APIException, AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('core')


class AppException(APIException):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str, status_code: int = 500, code: str = 'error'):
        self.status_code = status_code
        self.detail = {'message': message, 'code': code}
        super().__init__(detail=message)


class BadRequestException(AppException):
    def __init__(self, message: str = 'Bad request', code: str = 'bad_request'):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, code)


class UnauthorisedException(AppException):
    def __init__(self, message: str = 'Unauthorised', code: str = 'unauthorised'):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, code)


class ForbiddenException(AppException):
    def __init__(self, message: str = 'Forbidden', code: str = 'forbidden'):
        super().__init__(message, status.HTTP_403_FORBIDDEN, code)


class NotFoundException(AppException):
    def __init__(self, resource: str = 'Resource', code: str = 'not_found'):
        super().__init__(f'{resource} not found', status.HTTP_404_NOT_FOUND, code)


class ConflictException(AppException):
    def __init__(self, message: str = 'Conflict', code: str = 'conflict'):
        super().__init__(message, status.HTTP_409_CONFLICT, code)


class AccountLockedException(AppException):
    def __init__(self, minutes: int = 15):
        super().__init__(
            f'Account locked due to too many failed attempts. Try again in {minutes} minutes.',
            status.HTTP_429_TOO_MANY_REQUESTS,
            'account_locked',
        )


def custom_exception_handler(exc: Exception, context: Any) -> Response:
    """
    Override DRF's default exception handler to:
    1. Convert all exceptions to our standard envelope
    2. Log all 5xx errors for investigation
    3. Never expose internal details in production
    """

    # Convert Django's built-in exceptions to DRF ones
    if isinstance(exc, Http404):
        exc = NotFoundException()
    elif isinstance(exc, DjangoValidationError):
        exc = BadRequestException(
            message='; '.join(exc.messages) if hasattr(exc, 'messages') else str(exc)
        )

    # Get DRF's default response first
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code

        # Log server errors
        if status_code >= 500:
            logger.error(
                'Server error',
                extra={
                    'exception': str(exc),
                    'status_code': status_code,
                    'view': str(context.get('view', '')),
                },
                exc_info=True,
            )

        # Normalise error shape to our envelope
        error_data = response.data

        if isinstance(error_data, dict):
            if 'detail' in error_data:
                message = str(error_data['detail'])
            else:
                message = json.dumps({k: str(v) for k, v in error_data.items()})
        elif isinstance(error_data, list):
            message = '; '.join(str(e) for e in error_data)
        elif isinstance(error_data, str):
            message = error_data
        else:
            message = 'An error occurred'

        response.data = {
            'success': False,
            'error': {
                'message': message,
                'code': getattr(exc, 'code', 'error'),
            },
        }

    return response


def api_404_handler(request, exception=None):
    """Handle 404 errors for API endpoints by returning JSON."""
    return JsonResponse(
        {
            'success': False,
            'error': {
                'message': 'Endpoint not found',
                'code': 'not_found',
            },
        },
        status=404,
    )


def api_500_handler(request):
    """Handle 500 errors for API endpoints by returning JSON."""
    logger.error(
        'Server error',
        extra={'path': request.path},
        exc_info=True,
    )
    return JsonResponse(
        {
            'success': False,
            'error': {
                'message': 'Internal server error',
                'code': 'server_error',
            },
        },
        status=500,
    )

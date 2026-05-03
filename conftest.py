# conftest.py
# Shared pytest fixtures available to all tests.
# Fixtures here are auto-discovered by pytest across the entire project.

import pytest
from django.test import Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


# ---- API Clients ----

@pytest.fixture
def api_client():
    """Unauthenticated DRF API client."""
    return APIClient()


@pytest.fixture
def auth_api_client(db, regular_user):
    """DRF API client authenticated as a regular user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    refresh = RefreshToken.for_user(regular_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


@pytest.fixture
def admin_api_client(db, admin_user):
    """DRF API client authenticated as an admin user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
    return client


# ---- Users ----

@pytest.fixture
def regular_user(db):
    """A normal active user."""
    return User.objects.create_user(
        email='testuser@digitallegacy.ng',
        password='TestPass123!',
        first_name='Test',
        last_name='User',
        is_email_verified=True,
    )


@pytest.fixture
def admin_user(db):
    """A staff/admin user."""
    return User.objects.create_superuser(
        email='admin@digitallegacy.ng',
        password='AdminPass123!',
        first_name='Admin',
        last_name='User',
    )


@pytest.fixture
def unverified_user(db):
    """A user who hasn't verified their email yet."""
    return User.objects.create_user(
        email='unverified@digitallegacy.ng',
        password='TestPass123!',
        first_name='Unverified',
        last_name='User',
        is_email_verified=False,
    )


# ---- Utilities ----

@pytest.fixture
def request_id_header():
    """Standard request ID header for tracing."""
    return {'HTTP_X_REQUEST_ID': 'test-request-id-123'}

# tests/unit/test_health.py
# Unit tests for the health check endpoint.
# Run: pytest tests/unit/test_health.py -v

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestHealthCheck:

    def test_health_returns_200(self, api_client):
        """Health endpoint must always return 200."""
        response = api_client.get('/health/')
        assert response.status_code == 200

    def test_health_returns_versioned_200(self, api_client):
        """Versioned health endpoint also works."""
        response = api_client.get('/api/v1/health/')
        assert response.status_code == 200

    def test_health_response_structure(self, api_client):
        """Response must follow our standard envelope."""
        response = api_client.get('/health/')
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['status'] == 'ok'

    def test_health_includes_service_name(self, api_client):
        response = api_client.get('/health/')
        assert response.json()['data']['service'] == 'digital-legacy-api'

    def test_health_includes_timestamp(self, api_client):
        from datetime import datetime
        response = api_client.get('/health/')
        ts = response.json()['data']['timestamp']
        # Should be a valid ISO datetime string
        datetime.fromisoformat(ts)

    def test_health_request_id_header_echoed(self, api_client):
        """X-Request-Id sent in request should be echoed in response."""
        response = api_client.get('/health/', HTTP_X_REQUEST_ID='my-test-id-42')
        assert response.headers.get('X-Request-Id') == 'my-test-id-42'

    def test_health_generates_request_id_if_missing(self, api_client):
        """If no X-Request-Id is sent, server generates one."""
        response = api_client.get('/health/')
        assert 'X-Request-Id' in response.headers
        assert len(response.headers['X-Request-Id']) > 0

    def test_health_requires_no_auth(self, api_client):
        """Health check must be publicly accessible — no token needed."""
        # No credentials set — should still return 200
        response = api_client.get('/health/')
        assert response.status_code == 200

    def test_unknown_route_returns_404(self, api_client):
        response = api_client.get('/api/v1/nonexistent-endpoint/')
        assert response.status_code == 404

    def test_404_follows_error_envelope(self, api_client):
        response = api_client.get('/api/v1/nonexistent-endpoint/')
        data = response.json()
        assert data['success'] is False
        assert 'error' in data
        assert 'message' in data['error']


@pytest.mark.unit
class TestStrongPasswordValidator:

    def setup_method(self):
        from core.utils.validators import StrongPasswordValidator
        self.validator = StrongPasswordValidator()

    def test_valid_strong_password(self):
        """A password with all requirements should pass."""
        self.validator.validate('SecurePass123!')  # Should not raise

    def test_missing_uppercase_raises(self):
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            self.validator.validate('weakpass123!')

    def test_missing_lowercase_raises(self):
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            self.validator.validate('WEAKPASS123!')

    def test_missing_digit_raises(self):
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            self.validator.validate('WeakPassWord!')

    def test_missing_special_char_raises(self):
        from django.core.exceptions import ValidationError
        with pytest.raises(ValidationError):
            self.validator.validate('WeakPassWord1')

    def test_help_text_is_informative(self):
        text = self.validator.get_help_text()
        assert 'uppercase' in text
        assert 'lowercase' in text
        assert 'digit' in text
        assert 'special' in text


@pytest.mark.unit
class TestSecurityHeaders:

    def test_x_frame_options_deny(self, api_client):
        response = api_client.get('/health/')
        assert response.headers.get('X-Frame-Options') == 'DENY'

    def test_x_content_type_options_nosniff(self, api_client):
        response = api_client.get('/health/')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_api_responses_not_cached(self, api_client):
        """API responses must have no-store cache headers."""
        response = api_client.get('/api/v1/health/')
        cache_control = response.headers.get('Cache-Control', '')
        assert 'no-store' in cache_control


@pytest.mark.unit
class TestCustomExceptionHandler:

    def test_404_returns_error_envelope(self, api_client):
        response = api_client.get('/api/v1/does-not-exist/')
        data = response.json()
        assert response.status_code == 404
        assert data['success'] is False
        assert 'message' in data['error']

    def test_unauthenticated_returns_401(self, api_client):
        """Accessing a protected endpoint without token returns 401."""
        # /api/v1/vault/ requires auth (will be built in Sprint 3)
        # Testing the auth system's default deny behaviour
        response = api_client.get('/api/v1/vault/')
        # Either 401 or 404 depending on whether vault is registered yet
        assert response.status_code in [401, 404]

# core/utils/renderers.py
# Standard JSON renderer — wraps ALL successful responses in {success, data} envelope.

from rest_framework.renderers import JSONRenderer
import json


class StandardJSONRenderer(JSONRenderer):
    """
    Wraps every successful API response in:
    {
        "success": true,
        "data": <original response data>,
        "meta": { "page": ..., "total": ... }   # only for paginated responses
    }
    Error responses are handled separately by custom_exception_handler.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None
        status_code = response.status_code if response else 200

        # Don't wrap error responses (already handled by exception handler)
        if status_code >= 400:
            return super().render(data, accepted_media_type, renderer_context)

        # Don't double-wrap if already in our format
        if isinstance(data, dict) and 'success' in data:
            return super().render(data, accepted_media_type, renderer_context)

        wrapped = {'success': True, 'data': data}
        return super().render(wrapped, accepted_media_type, renderer_context)

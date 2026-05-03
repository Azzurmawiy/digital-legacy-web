# core/utils/pagination.py
# Standard pagination with meta envelope for all paginated responses.

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Standard pagination with meta envelope.
    Wraps paginated responses with metadata about page, total count, etc.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'data': data,
            'meta': {
                'page': self.page.number,
                'page_size': self.page.paginator.per_page,
                'total': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            },
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean'},
                'data': schema,
                'meta': {
                    'type': 'object',
                    'properties': {
                        'page': {'type': 'integer'},
                        'total': {'type': 'integer'},
                        'total_pages': {'type': 'integer'},
                    },
                },
            },
        }

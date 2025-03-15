from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from foodgram_backend.constant import PAGE_SIZE


class Pagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE


class LimitRecipesPagination(PageNumberPagination):
    page_size_query_param = 'recipes_limit'
    max_page_size = PAGE_SIZE

    def get_paginated_response(self, data):
        recipe_limit = int(self.request.query_params['recipes_limit'])
        for obj in data:
            obj['recipes'] = obj['recipes'][:recipe_limit]
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

from rest_framework.pagination import PageNumberPagination

from foodgram_backend.constant import PAGE_SIZE


class Pagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAGE_SIZE
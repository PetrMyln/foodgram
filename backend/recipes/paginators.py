from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response


class CustomPagination(LimitOffsetPagination):
    #page_size_query_param = 'limit'  # используем параметр 'limit' вместо 'page_size'
    #max_page_size = 100  # максимальное количество объектов на странице

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data,
            'limit': self.get_page_size(self.request)  # добавляем текущий размер страницы
        })

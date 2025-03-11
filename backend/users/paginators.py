from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        obj_cont = list(self.request.query_params.items())
        if obj_cont and obj_cont[0][0] == 'limit':
            cont_on_page = int(obj_cont[0][1])
            self.page.paginator.count = cont_on_page
            data = data[:cont_on_page]
        return Response(
            {
                'count': self.page.paginator.count,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'results': data
            }
        )

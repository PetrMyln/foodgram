import generics
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from users.models import User
from users.serializers import UserSerializer, AuthSerializer, TokenSerializer




class UserViewSet(ModelViewSet):
    queryset = User.objects.order_by('username')
    serializer_class = UserSerializer
    #permission_classes = (UserPermission,)

    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    pagination_class = PageNumberPagination

    @action(
        methods=['GET', 'PATCH'], detail=False, url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_update_me(self, request):
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'PATCH':
            serializer.validated_data.pop('role', None)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)





class SignUpView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Код подтверждения',
            f'Ваш код - {confirmation_code}',
            settings.SENDER_EMAIL,
            [request.data.get('email')]
        )

        return Response(serializer.data, status=status.HTTP_200_OK)




class TokenView(APIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = {'token': str(AccessToken.for_user(
            serializer.validated_data))}
        return Response(token, status=status.HTTP_200_OK)



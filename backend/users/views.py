from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import update_session_auth_hash
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.authtoken.models import Token



from users.models import User, Follow
from users.permissions import UserPermission, UserProfilePermission
from users.serializers import (
    UsersSerializer,
)





class ProfileView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'id'


class MyView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            serializer = UsersSerializer(user)
            return Response(serializer.data)
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


class MyAvatarView(generics.UpdateAPIView):
    permission_classes = [UserPermission]
    serializer_class = UsersSerializer

    def put(self, request, *args, **kwargs):
        if not request.data:
            raise ValidationError(
                {f'avatar': ["Обязательное поле."]})
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({'avatar': serializer.data['avatar']})

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.avatar = None
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except ValidationError as exc:
            exc.detail.update({
                'Erore': 'Пожалуйста, загрузите корректный файл изображения.'
            })
            raise exc
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)

    def perform_update(self, serializer):
        serializer.save()




class SubscriptionListView(generics.ListAPIView):
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following__follower_id=self.request.user.pk)


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user = get_object_or_404(User, id=id)
        subscriber = request.user
        if user == subscriber:
            return Response(
                {'Ошибка': 'Подписываться на самого себя запрещено.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        _, created = Follow.objects.get_or_create(follower=subscriber, user=user)
        if created:
            serializer = UsersSerializer(
                User.objects.get(username=user),
                context={'subscriber': subscriber.pk}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'Ошибка': 'Выуже подписанны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id):
        get_object_or_404(Follow, user_id=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

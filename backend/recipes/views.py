from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
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
from rest_framework.renderers import JSONRenderer
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipes
from recipes.serializers import IngredientSerializer, TagSerializer, RecipesSerializer
from users.models import User, Follow
from users.permissions import UserPermission
from django_filters.rest_framework import DjangoFilterBackend


class IngredientsMain:
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permissions = (permissions.AllowAny,)


class IngredientsView(IngredientsMain, generics.ListAPIView):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    renderer_classes = [JSONRenderer]
    search_fields = ['^name']
    pagination_class = None


class IngredientsDetailView(IngredientsMain, generics.RetrieveAPIView):
    pass


class TagsMain:
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permissions = (permissions.AllowAny,)


class TagsView(TagsMain, generics.ListAPIView):
    pass


class TagsDetailView(TagsMain, generics.RetrieveAPIView):
    pass




class RecipesListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RecipesSerializer
    queryset = Recipes.objects.all()


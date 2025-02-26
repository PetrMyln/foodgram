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

from foodgram_backend.permissions import UserOrReadOnly
from recipes.models import Ingredient, Tag, Recipes, ShoppingCart, FavoriteRecipe
from recipes.serializers import IngredientSerializer, TagSerializer, RecipesSerializer, ShoppingSerializer, \
    FavoriteRecipeSerializer, RecipesPostSerializer
from users.models import User, Follow
from users.permissions import UserPermission
from django_filters.rest_framework import DjangoFilterBackend


class IngredientsMain:
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class IngredientsView(IngredientsMain, generics.ListAPIView):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    renderer_classes = [JSONRenderer]
    search_fields = ['^name']
    pagination_class = PageNumberPagination


class IngredientsDetailView(IngredientsMain, generics.RetrieveAPIView):
    pass


class TagsMain:
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class TagsView(TagsMain, generics.ListAPIView):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    renderer_classes = [JSONRenderer]
    search_fields = ['^name']
    pagination_class = PageNumberPagination


class TagsDetailView(TagsMain, generics.RetrieveAPIView):
    pass


class RecipesMain:
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RecipesSerializer, RecipesPostSerializer
    queryset = Recipes.objects.all()
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipesPostSerializer
        return RecipesSerializer


class RecipesListCreateView(RecipesMain, generics.ListCreateAPIView):
    pass


class RecipesDetailUpdaateDeleteView(
    RecipesMain,
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [UserOrReadOnly]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


########################
class GetLinkView(APIView):
    def get(self, request, recipe_id, format=None):
        pass


class ShoppingCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = get_object_or_404(User, id=self.request.user.pk)
        recipe = get_object_or_404(Recipes, id=request.parser_context['kwargs']['pk'])
        obj, created = ShoppingCart.objects.get_or_create(
            recipe=recipe,
            user=user,
            name=recipe.name,
            image=recipe.image,
            cooking_time=recipe.cooking_time
        )
        if created:
            serializer = ShoppingSerializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'Ошибка': 'Рецепт уже добавле в корзину.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        get_object_or_404(ShoppingCart, recipe=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = get_object_or_404(User, id=self.request.user.pk)
        recipe = get_object_or_404(Recipes, id=request.parser_context['kwargs']['pk'])
        obj, created = FavoriteRecipe.objects.get_or_create(
            recipe=recipe,
            user=user,
            name=recipe.name,
            image=recipe.image,
            cooking_time=recipe.cooking_time
        )
        if created:
            serializer = FavoriteRecipeSerializer(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'Ошибка': 'Рецепт уже добавле в избранное.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        get_object_or_404(FavoriteRecipe, recipe=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IndexListView(generics.ListAPIView):
    pagination_class = PageNumberPagination
    queryset = Recipes.objects.all()[:5]
    serializer_class = RecipesSerializer
    permission_classes = [permissions.AllowAny]

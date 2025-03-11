from random import choice
from string import ascii_letters, digits

from django.shortcuts import get_object_or_404, redirect
from rest_framework import filters, permissions, status

from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.permissions import IsAuthenticated

from rest_framework.renderers import JSONRenderer

from rest_framework import viewsets

from recipes.models import Ingredient, Tag, Recipes, ShoppingCart, FavoriteRecipe, RecipesIngredient, ShortLink
from users.paginators import CustomPagination
from recipes.serializers import IngredientSerializer, TagSerializer, RecipesSerializer, ShoppingSerializer, \
    FavoriteRecipeSerializer, RecipesPostSerializer
from users.models import User
from users.permissions import AuthorOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ['^name']
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class TagsView(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    renderer_classes = [JSONRenderer]
    search_fields = ['^name']
    pagination_class = None


class RecipesView(viewsets.ModelViewSet):
    http_method_names = 'get', 'post', 'patch', 'delete'
    permission_classes = [AuthorOrReadOnly]
    serializer_class = RecipesSerializer, RecipesPostSerializer
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('author',)
    search_fields = ('tags', 'ingredients')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipesPostSerializer
        return RecipesSerializer

    def get_queryset(self):
        queryset = Recipes.objects.all()
        tags = self.request.query_params.getlist('tags')
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        is_favorited = self.request.query_params.get('is_favorited')
        if is_in_shopping_cart and self.request.user.is_authenticated:
            recipes = Recipes.objects.prefetch_related(
                'shopping_cart').filter(shopping_cart__user=self.request.user)
            return recipes
        if is_favorited and self.request.user.is_authenticated:
            recipes = Recipes.objects.prefetch_related(
                'favorite_rec').filter(
                favorite_rec__user=self.request.user, tags__slug__in=tags).distinct()
            return recipes
        if tags:
            return queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user != instance.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class GetLinkView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk, format=None):
        full_url = request.build_absolute_uri()[:-10]
        recipe = Recipes.objects.get(
            pk=request.parser_context['kwargs'].get('pk')
        )
        obj_rec, created = ShortLink.objects.get_or_create(recipe=recipe)
        if not created:
            return Response({"short-link": obj_rec.short_link})
        characters = ascii_letters + digits
        response = ''.join(choice(characters) for _ in range(3))
        url = request.build_absolute_uri().split('/api/')[0] + '/s/' + response
        obj_rec.short_link = url
        obj_rec.original_url = full_url
        obj_rec.save()
        return Response({"short-link": obj_rec.short_link})

class RedirectView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, short_code):
        get_object_or_404(ShortLink, short_link=short_code)
        link = ShortLink.objects.get(short_link=short_code)
        return redirect(link.original_link)










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

        get_object_or_404(Recipes, id=pk)

        rule_to_delete_recipe = ShoppingCart.objects.filter(
            user=request.user.pk, recipe=pk
        )

        if not rule_to_delete_recipe.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        rule_to_delete_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeView(APIView):
    permission_classes = [AuthorOrReadOnly]

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
        get_object_or_404(Recipes, id=pk)
        rule_to_delete_recipe = FavoriteRecipe.objects.filter(
            user=request.user.pk, recipe=pk
        )
        if not rule_to_delete_recipe.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        rule_to_delete_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartView(APIView):

    def get(self, request):
        shopping = ShoppingCart.objects.select_related('recipe')
        all_recipe = []
        for shop in shopping:
            all_recipe.append(shop.recipe.pk)
        ings = RecipesIngredient.objects.select_related('ingredient')
        some_dict = dict()
        for i in ings:

            if i.recipe is None or i.recipe is None:
                continue
            if i.recipe.pk in all_recipe:
                some_dict.setdefault(
                    i.ingredient.name, {}
                ).setdefault(i.ingredient.measurement_unit, []
                             ).append(i.amount)

        all_str = []
        for key, value in some_dict.items():
            for weigt, cnt in value.items():
                string = f'{key} {str(sum(map(int, cnt)))} {weigt}\n'
                all_str.append(string)

        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        for item in all_str:
            response.write(f"{item}")
        return response

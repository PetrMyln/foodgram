from random import choice
from string import ascii_letters, digits

from django.shortcuts import get_object_or_404, redirect
from djoser.views import UserViewSet as DjoserUserViewSet
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets

from api.paginators import Pagination, LimitRecipesPagination
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipesSerializer,
    RecipesPostSerializer,
    UsersSerializer,
    ShoppingSerializer,
    FavoriteSerializer
)
from recipes.models import (
    Ingredient,
    Tag,
    Recipes,
    ShoppingCart,
    FavoriteRecipe,
    RecipesIngredient,
    ShortLink
)

from api.permissions import AuthorOrReadOnly
from api.filters import IngredientFilter, RecipesFilter
from api.permissions import AuthorOrModeratorOrReadOnly
from users.models import User, Follow
from api.serializers import SubscribeSerializer


class UserViewSet(DjoserUserViewSet):
    pagination_class = Pagination

    def make_serializer(self, instance, data, partial=True):
        return self.get_serializer(
            instance,
            data=data,
            partial=partial
        )

    def check_before_update_delete(self, serializer):
        serializer.is_valid(serializer)
        self.perform_update(serializer)

    @action(
        detail=False,
        url_path='me',
        permission_classes=[AuthorOrModeratorOrReadOnly],
        serializer_class=UsersSerializer
    )
    def me(self, request, *args, **kwargs):
        instance = request.user
        if not instance.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[AuthorOrModeratorOrReadOnly],
        serializer_class=UsersSerializer
    )
    def avatar(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.make_serializer(instance, request.data)
        if request.method == 'PUT':
            self.check_before_update_delete(serializer)
            return Response({'avatar': serializer.data['avatar']})
        instance.avatar = ''
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
        serializer_class=SubscribeSerializer
    )
    def subscriptions(self, request, *args, **kwargs):
        if 'recipes_limit' in request.query_params:
            self.pagination_class = LimitRecipesPagination
        queryset = User.objects.filter(
            following__follower_id=self.request.user.pk)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
        serializer_class=SubscribeSerializer
    )
    def subscribe(self, request, id, **kwargs):

        subscriber = request.user
        user = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(
            follower=subscriber, user=user
        )
        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'Ошибка': 'Вы не подписаны на этого пользователя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SubscribeSerializer(
            user,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if subscription.exists():
            return Response(
                {'Ошибка': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.create(follower=subscriber, user=user)
        serializer = SubscribeSerializer(user, context={'request': request})
        if 'recipes_limit' in request.query_params:
            recipe_limit = int(self.request.query_params['recipes_limit'])
            respons_data = dict(serializer.data)
            respons_data['recipes'] = respons_data['recipes'][:recipe_limit]
            return Response(respons_data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IngredientsView(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
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
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer, RecipesPostSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipesFilter
    search_fields = ('tags', 'ingredients')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipesPostSerializer
        return RecipesSerializer

    @action(
        detail=True,
        url_path='get-link',
        permission_classes=[permissions.AllowAny],
        serializer_class=SubscribeSerializer
    )
    def get_link(self, request, pk, format=None):
        full_url = request.build_absolute_uri()[:-10]
        recipe = Recipes.objects.get(
            pk=request.parser_context['kwargs'].get('pk')
        )
        obj_rec, created = ShortLink.objects.get_or_create(recipe=recipe)
        if not created:
            return Response({"short-link": obj_rec.short_link})
        characters = ascii_letters + digits

        while True:
            response = ''.join(choice(characters) for _ in range(3))
            url = request.build_absolute_uri().split(
                '/api/')[0]
            url = url + '/s/' + response
            if ShortLink.objects.filter(short_link=url).exists():
                continue
            obj_rec.short_link = url
            obj_rec.original_url = full_url.replace('/api', '')
            obj_rec.save()
            break
        return Response({"short-link": obj_rec.short_link})

    def shop_and_favorite(self, request, pk, model, serializer, item):
        user = get_object_or_404(User, id=self.request.user.pk)
        recipe = get_object_or_404(Recipes, id=pk)
        if request.method == 'DELETE':
            rule_to_delete = model.objects.filter(
                user=request.user.pk, recipe=pk
            )
            if rule_to_delete.delete()[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        obj, created = model.objects.get_or_create(
            recipe=recipe,
            user=user,
            name=recipe.name,
        )
        if created:
            serializer = serializer(obj)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'Ошибка': f'Рецепт уже добавле в {item}.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def get_shopping_cart(self, request, pk):
        return self.shop_and_favorite(
            request,
            pk,
            ShoppingCart,
            ShoppingSerializer,
            'корзину'
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def get_favorite(self, request, pk):
        return self.shop_and_favorite(
            request,
            pk,
            FavoriteRecipe,
            FavoriteSerializer,
            'избранное'
        )

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def get_download_shopping_cart(self, request):
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
        response['Content-Disposition'] = (
            'attachment; filename='
            '"shopping_list.txt"')
        for item in all_str:
            response.write(f"{item}")
        return response


class RedirectView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, link):
        link = ShortLink.objects.filter(short_link__endswith=link).first()
        return redirect(link.original_url, permanent=False)

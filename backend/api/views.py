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
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Ingredient,
    Tag,
    Recipes,
    ShoppingCart,
    FavoriteRecipe,
    RecipesIngredient,
    ShortLink
)
from api.paginators import CustomPagination
from api.serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipesSerializer,
    ShoppingSerializer,
    FavoriteRecipeSerializer,
    RecipesPostSerializer
)

from api.permissions import AuthorOrReadOnly
from api.filters import IngredientFilter, RecipesFilter
from api.permissions import AuthorOrModeratorOrReadOnly
from users.models import User, Follow
from api.serializers import SubscribeSerializer


class UserViewSet(DjoserUserViewSet):
    pagination_class = CustomPagination

    def make_serializer(self, instance, data, partial=True):
        return self.get_serializer(
            instance,
            data=data,
            partial=partial
        )

    def check_before_update_delete(self, serializer):
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[AuthorOrModeratorOrReadOnly]
    )
    def avatar(self, request, *args, **kwargs):
        instance = self.request.user
        if request.method == 'PUT':
            if not request.data:
                raise ValidationError(
                    {'avatar': ["Обязательное поле."]})
            serializer = self.make_serializer(instance, request.data)
            self.check_before_update_delete(serializer)
            return Response({'avatar': serializer.data['avatar']})
        instance.avatar = ''
        try:
            serializer = self.make_serializer(instance, request.data)
            self.check_before_update_delete(serializer)
        except ValidationError as exc:
            exc.detail.update({
                'Ошибка': 'Пожалуйста, загрузите '
                          'корректный файл изображения.'
            })
            raise exc
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=[IsAuthenticated],
        serializer_class=SubscribeSerializer
    )
    def subscriptions(self, request, *args, **kwargs):
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
        user = get_object_or_404(User, id=id)
        subscriber = request.user
        if user == subscriber:
            return Response(
                {
                    'Ошибка': 'Подписка и отписка на самого себя запрещена.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            rule_is_sub_exists = Follow.objects.filter(
                follower_id=request.user.pk, user_id=id)
            if not rule_is_sub_exists.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            rule_is_sub_exists.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        check_value_query_params = list(request.query_params.items())
        if check_value_query_params:
            query_params_value = list(request.query_params.items())[0]
        else:
            query_params_value = None
        _, created = Follow.objects.get_or_create(
            follower=subscriber, user=user
        )
        if created:
            serializer = SubscribeSerializer(
                User.objects.get(username=user),
                context={
                    'subscriber': subscriber.pk,
                    'post': query_params_value
                }
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {'Ошибка': 'Выуже подписанны на этого пользователя.'},
            status=status.HTTP_400_BAD_REQUEST
        )


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
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipesFilter
    search_fields = ('tags', 'ingredients')

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipesPostSerializer
        return RecipesSerializer

    def create(self, request, *args, **kwargs):
        # Для ревьювера.
        # уже передаю автора в сериализатор двумя строчками ниже
        # у меня в сериализаторе RecipesPostSerializer
        # author = UsersSerializer(default=serializers.CurrentUserDefault())
        # может тогда вообще не передавать ?
        #  и оставить вот так serializer.save()
        #  если опять у меня ошибка, направте поточнее. спасибо
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        recipe = get_object_or_404(
            Recipes,
            id=request.parser_context['kwargs']['pk']
        )
        if request.method == 'DELETE':
            rule_to_delete = model.objects.filter(
                user=request.user.pk, recipe=pk
            )
            if not rule_to_delete.exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            rule_to_delete.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        obj, created = model.objects.get_or_create(
            recipe=recipe,
            user=user,
            name=recipe.name,
            image=recipe.image,
            cooking_time=recipe.cooking_time
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
            FavoriteRecipeSerializer,
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

from django_filters import (
    filters,
    FilterSet,
    CharFilter,
)
from recipes.models import Ingredient, Recipes, Tag


class IngredientFilter(FilterSet):
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.NumberFilter(method='get_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='get_in_shopping_cart')

    class Meta:
        model = Recipes
        fields = (
            'author',
            'tags',
            'is_in_shopping_cart',
            'is_favorited',
        )

    def get_favorited(self, *args, **kwargs):
        queryset = Recipes.objects.all()
        tags = self.request.query_params.getlist('tags')
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited and self.request.user.is_authenticated:
            recipes = Recipes.objects.prefetch_related(
                'favorite_rec').filter(
                favorite_rec__user=self.request.user
            )
            if tags:
                return recipes.filters(tags__slug__in=tags)
            return recipes
        return queryset

    def get_in_shopping_cart(self, queryset, name, value):
        queryset = Recipes.objects.all()
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart and self.request.user.is_authenticated:
            recipes = Recipes.objects.prefetch_related(
                'shopping_cart').filter(
                shopping_cart__user=self.request.user
            )
            return recipes
        return queryset

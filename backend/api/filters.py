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
        if args[1] and self.request.user.is_authenticated:
            recipes = args[0].filter(
                favorite_rec__user=self.request.user
            )
            return recipes
        return args[0]

    def get_in_shopping_cart(self, *args, **kwargs):
        if args[1] and self.request.user.is_authenticated:
            recipes = args[0].filter(
                shopping_cart__user=self.request.user
            )
            return recipes
        return args[0]

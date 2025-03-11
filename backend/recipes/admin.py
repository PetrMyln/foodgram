from django.contrib import admin

from recipes.models import (
    Ingredient,
    Tag,
    Recipes,
    FavoriteRecipe,
    RecipesIngredient,
    ShoppingCart,
    RecipeTag,
    ShortLink

)

class ShortLinkAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'short_link','original_url')
    search_fields = ('recipe',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_filter = ('name',)


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorites_recipe_count',
    )
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
    ordering = ('-pub_date',)

    def favorites_recipe_count(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    #
    favorites_recipe_count.short_description = "Количество в избранном"

    @admin.display(description='Ингредиентыfff')
    def get_ing_list(self, obj):
        sqn_of_genre = Ingredient.objects.all()
        genre_sqn = [curent for curent in sqn_of_genre]
        return genre_sqn if genre_sqn else 'Добавте жанры к произведению'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'image', 'cooking_time')


class RecipesIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount')


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')
    search_fields = ('tag', 'recipe')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'cooking_time', 'image')
    search_fields = ('user', 'recipe')




admin.site.register(ShortLink, ShortLinkAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipesIngredient, RecipesIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipes, RecipesAdmin)

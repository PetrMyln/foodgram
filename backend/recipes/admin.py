from django.contrib import admin

# Register your models here.

from recipes.models import (
    Ingredient,
    Tag,
    Recipes,
    FavoriteRecipe,
    RecipesIngredient,
    ShoppingCart,
    RecipeTag


)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'image',
        'favorites_recipe_count',
        'pub_date'
    )
    search_fields = ('title', 'author__username')
    list_filter = ('tags',)
    ordering = ('-pub_date',)
    list_display_links = ('name',)
    filter_horizontal = ('ingredients',)

    def favorites_recipe_count(self, obj):
        return FavoriteRecipe.objects.filter(recipe=obj).count()

    favorites_recipe_count.short_description = "Количество в избранном"




class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe','image', 'cooking_time')

class RecipesIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient','recipe','amount')


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')
    search_fields = ('tag', 'recipe')




class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'cooking_time', 'image')
    search_fields = ('user', 'recipe')


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipesIngredient, RecipesIngredientAdmin)
admin.site.register(FavoriteRecipe, FavoriteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipes, RecipesAdmin)


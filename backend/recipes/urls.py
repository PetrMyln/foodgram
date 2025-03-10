from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from recipes.views import (

    TagsView,
    GetLinkView, ShoppingCartView,
    FavoriteRecipeView,
    #IndexListView,
    RecipesView, IngredientsView, DownloadShoppingCartView,
)

router = DefaultRouter()
router.register('tags', TagsView)
router.register('ingredients', IngredientsView)
router.register('recipes', RecipesView)






recipes_patterns = [
    path('download_shopping_cart/',
         DownloadShoppingCartView.as_view(),
         name='dwnload-shopcart',
         ),
    path('<int:pk>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite-recipe'),
    path('<int:pk>/shopping_cart/',
         ShoppingCartView.as_view(), name='add-recipe-to-cart'),
    path(
        '<int:pk>/get-link/',
        GetLinkView.as_view(),
        name='get-short-link'
    ),

]

urlpatterns = [

    #path('ingredients/', include(ingredients_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('', include(router.urls)),
    #path('',IndexListView.as_view(), name='index'),

]

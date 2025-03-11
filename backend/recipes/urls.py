from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from recipes.views import (
    TagsView,
    GetLinkView,
    ShoppingCartView,
    FavoriteRecipeView,
    RecipesView,
    IngredientsView,
    DownloadShoppingCartView,
    RedirectView
)

router = DefaultRouter()
router.register('tags', TagsView, basename='tags')
router.register('ingredients', IngredientsView, basename='recipes')
router.register('recipes', RecipesView,  basename='ingredients')






recipes_patterns = [
    path('download_shopping_cart/',
         DownloadShoppingCartView.as_view(),
         name='cart',
         ),
    path('<int:pk>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite-recipe'),
    path('<int:pk>/shopping_cart/',
         ShoppingCartView.as_view(), name='cart-view'),
    path(
        '<int:pk>/get-link/',
        GetLinkView.as_view(),
        name='get-short-link'
    ),
    path('s/<str:short_code>/', RedirectView.as_view(), name='redirect'),

]

urlpatterns = [

    #path('ingredients/', include(ingredients_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('', include(router.urls)),
    #path('',IndexListView.as_view(), name='index'),

]

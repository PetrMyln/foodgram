from django.urls import include, path
from rest_framework import routers

from recipes.views import (
    IngredientsView,
    IngredientsDetailView, TagsView, TagsDetailView,
    RecipesListCreateView,
    RecipesDetailUpdaateDeleteView,
    GetLinkView, ShoppingCartView,
    FavoriteRecipeView,
    IndexListView
)

ingredients_patterns = [
    path('', IngredientsView.as_view(), name='ingredients-list'),
    path('<int:pk>/', IngredientsDetailView.as_view(), name='ingredients-detail'),
]
tags_patterns = [
    path('', TagsView.as_view(), name='tags-list'),
    path('<int:pk>/', TagsDetailView.as_view(), name='tags-detail'),
]

recipes_patterns = [
    path('', RecipesListCreateView.as_view(), name='recipes-list'),
    path('<int:pk>/favorite/',
         FavoriteRecipeView.as_view(), name='favorite-recipe'),
    path('<int:pk>/shopping_cart/',
         ShoppingCartView.as_view(), name='add-recipe-to-cart'),
    path('<int:pk>/get-link/', GetLinkView.as_view(), name='get-short-link'),
    path('<int:pk>/',
         RecipesDetailUpdaateDeleteView.as_view(), name='recipes-detail'),
]

urlpatterns = [

    path('ingredients/', include(ingredients_patterns)),
    path('tags/', include(tags_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('',IndexListView.as_view(), name='index')
]

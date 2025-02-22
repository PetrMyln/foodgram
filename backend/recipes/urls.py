from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientsView, IngredientsDetailView
from users.views import (
    SignUpView,
    TokenView,
    ProfileView,
    MyView,
    MyAvatarView,
    SetPasswordView,
)




ingredients_patterns = [
    path('', IngredientsView.as_view(), name='ingredients-list'),
    path('<int:pk>/', IngredientsDetailView.as_view(), name='ingredients-detail'),



]


urlpatterns = [
    #path('ingredients/', IngredientsView.as_view(), name='ingredients-list'),
    path('ingredients/', include(ingredients_patterns)),

]
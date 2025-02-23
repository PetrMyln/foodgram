import base64

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.hashers import make_password, check_password
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from foodgram_backend.constant import LENGTH_TEXT, LENGTH_USERNAME
from foodgram_backend.validators import validate_username, ValidationError
from recipes.models import Ingredient, Tag, Recipes, RecipesIngredient, RecipeTag
from users.serializers import Base64ImageField, UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class RecipeTagSerializer(serializers.Serializer):
    tag = TagSerializer()

    class Meta:
        model = RecipeTag
        fields = 'tag',


class IngredientSerializer(serializers.ModelSerializer):
    #name = serializers.CharField(required=False)
    #amount = serializers.IntegerField(read_only=True)
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.Serializer):
    #ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    #ingredients = serializers.IntegerField(source='ingredient')
    #recipes = serializers.IntegerField(read_only=True)
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = '__all__'
        #fields = 'id', 'amount',





class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    #author = UserSerializer(default=serializers.CurrentUserDefault())
    author =serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )



    class Meta:
        model = Recipes
        fields = ['id','ingredients','tags','name','author','image','text','cooking_time']
        #fields = '__all__'
        #read_only_fields = 'author',

    def create(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        print(tags_data)
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        #recipe.ingredients.set(ingredients_data)
        #print(ingredients_data[0]['id'])
       # print(ingredients_data[0]['amount'])
        for ingredient_data in ingredients_data:
            print(ingredient_data['amount'],1111111111111111111111111111111)
            RecipesIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient_data['id']),
                amount = ingredient_data['amount'],
            )

            #print(RecipesIngredient.objects.all()[0].id)
        return recipe

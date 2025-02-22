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
from users.serializers import Base64ImageField




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
    #amount = serializers.IntegerField(source='value', required=False)
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.Serializer):
    #ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    ingredient = IngredientSerializer()
    #amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = '__all__'



class RecipesSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients =  serializers.PrimaryKeyRelatedField(many=True,read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )


    class Meta:
        model = Recipes
        fields = ['id','ingredients','tags','author','name','image','text','cooking_time']
        #read_only_fields = 'author',

    def fcreate(self, validated_data):
        print(validated_data)
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipesIngredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe

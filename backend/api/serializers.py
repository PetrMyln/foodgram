import base64
from collections import Counter

from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.files.base import ContentFile
from django.contrib.auth.hashers import make_password
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from foodgram_backend.constant import LENGTH_TEXT, LENGTH_USERNAME
from users.models import User, Follow
from recipes.models import (
    Ingredient,
    Tag,
    Recipes,
    RecipesIngredient,
    ShoppingCart,
    FavoriteRecipe
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            form, imgstr = data.split(';base64,')
            ext = form.split('/')[-1]
            data = ContentFile(
                base64.b64decode(imgstr), name='image.' + ext
            )
        return super().to_internal_value(data)


class UsersSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def validate(self, attr):
        if not attr:
            raise ValidationError(
                {'avatar': "Обязательное поле."})
        return attr

    def get_is_subscribed(self, obj):
        user = obj.pk
        rule = (
                self.context.get('subscriber') is None
                and self.context.get('request') is None
        )
        if rule:
            return False
        if self.context.get('subscriber'):
            follower = self.context['subscriber']
            return Follow.objects.filter(
                user_id=user, follower_id=follower
            ).exists()
        if self.context.get('request') is not None:
            follower = self.context['request'].user.pk
        return Follow.objects.filter(
            user_id=user, follower_id=follower
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


from django.conf import settings


class FavoriteShoppingSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        return (f"{settings.SITE_URL}"
                f"{settings.MEDIA_URL}"
                f"{str(obj.recipe.image)}")

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time


class FavoriteSerializer(FavoriteShoppingSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingSerializer(FavoriteShoppingSerializer):
    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Значение должно быть больше 0'
            )
        return value


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UsersSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients')
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        ]
        read_only_fields = fields

    def get_is_favorited(self, obj):
        user = self.context['request'].user.pk
        recipe = obj.pk
        return FavoriteRecipe.objects.filter(
            user_id=user, recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user.pk
        recipe = obj.pk
        return ShoppingCart.objects.filter(
            user_id=user, recipe=recipe
        ).exists()


class PostRecipeIngredientSerializer(RecipeIngredientSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesPostSerializer(serializers.ModelSerializer):
    author = UsersSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True)
    ingredients = PostRecipeIngredientSerializer(
        many=True,
        required=True,

    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
    )
    name = serializers.CharField(required=True, max_length=256)
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages={
            'min_value': 'Значение должно быть не меньше 1'
        }
    )

    class Meta:
        model = Recipes
        fields = (
            'tags',
            'ingredients',
            'author',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        method = self.context['request'].method
        required_fields = {'ingredients', 'tags'}
        if method == 'POST':
            missing_fields = set(self.Meta.fields) - set(attrs.keys())
            if missing_fields:
                raise ValidationError(
                    f'Отсутствуют обязательные поля: {", ".join(missing_fields)}',
                    code=400
                )
        for field in required_fields:
            if not attrs.get(field):
                raise ValidationError(
                    f'Поле {field} не может быть пустым',
                    code=400
                )
        get_ingredient = attrs.get('ingredients')
        get_tag = attrs.get('tags')
        if get_ingredient:
            hashed_dicts = len(set(
                frozenset(d.items()) for d in get_ingredient)
            )

            if hashed_dicts != len(get_ingredient):
                raise ValidationError(
                    'Повторения в поле ingredients',
                    code=400
                )
        if get_tag:
            rule_tags = len(get_tag) == len(frozenset(get_tag))
            if not rule_tags:
                raise ValidationError(
                    'Повторения в поле tags',
                    code=400
                )
        return attrs

    def to_representation(self, instance):
        return RecipesSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data

    def add_tags_ingredients(self, ingredients, tags, model):
        recipeingredients_data = []
        for ingredient in ingredients:
            recipeingredients_data.append(
                RecipesIngredient(
                    recipe=model,
                    ingredient=ingredient['id'],
                    amount=ingredient['amount'])
            )
        RecipesIngredient.objects.bulk_create(recipeingredients_data)
        model.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get("request").user
        recipe = super().create(validated_data)
        self.add_tags_ingredients(ingredients, tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self.add_tags_ingredients(ingredients, tags, instance)
        return super().update(instance, validated_data)




class AuthSerializer(DjoserUserSerializer):

    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            password=make_password(validated_data.get('password')),
        )
        return user


class RecipeForSubcriber(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UsersSerializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    recipes = RecipeForSubcriber(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

        read_only_fields = ('email', 'username',)

    def validate(self, data):

        user = self.context['request'].user
        subscriber = self.instance
        if user == subscriber:
            raise serializers.ValidationError(
                {'Ошибка': 'Подписка и отписка на самого себя запрещена.'}
            )
        return data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        rule = 'post' in self.context.keys()
        if rule:
            if self.context['post'] is None:
                return representation
            cnt_recipes = int(self.context['post'][1])
            representation['recipes'] = representation['recipes'][:cnt_recipes]
            return representation
        recipe_limit = list(self.context.get('request').query_params.items())
        if recipe_limit and recipe_limit[0][0] == 'recipes_limit':
            cnt_recipes = int(recipe_limit[0][1])
            representation['recipes'] = representation['recipes'][:cnt_recipes]
            return representation
        return representation




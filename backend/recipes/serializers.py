from rest_framework import serializers


from foodgram_backend.validators import ValidationError
from recipes.models import (
    Ingredient,
    Tag, Recipes,
    RecipesIngredient,
    RecipeTag,
    ShoppingCart,
    FavoriteRecipe)
from users.serializers import Base64ImageField, UsersSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class ShoppingSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = ShoppingCart
        fields = ['id', 'name', 'image', 'cooking_time']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

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

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UsersSerializer(default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipe_ingredients')
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
    FIELDS = [
        'tags',
        'author',
        'ingredients',
        'image',
        'name',
        'text',
        'cooking_time'
    ]
    CHECK_FILED_TAGS = 'tags'

    author = UsersSerializer(default=serializers.CurrentUserDefault())
    image = Base64ImageField()
    ingredients = PostRecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)

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

    def check_ingredient(self, attrs):
        check_list_for_ingredient = []
        for c in attrs['ingredients']:
            if c['amount'] < 1:
                raise ValidationError(
                    message='Значение должно быть больше нуля',
                    code=400,
                )
            rule_for_ingredient = Ingredient.objects.filter(
                id=c['id'].pk
            ).exists()
            if not rule_for_ingredient:
                raise ValidationError(
                    message=f'Не существует ингредиент {c["id"]}',
                    code=400,
                )
            if c["id"] not in check_list_for_ingredient:
                check_list_for_ingredient.append(c['id'])
            else:
                raise ValidationError(
                    message=f'Вы указали два одинаковых ингредиента',
                    code=400,
                )
        return attrs

    def check_tags(self, attrs):
        rule_not_same_tags = len(
            attrs[self.CHECK_FILED_TAGS]) == len(
            set(attrs[self.CHECK_FILED_TAGS])
        )
        if not rule_not_same_tags:
            raise ValidationError(
                message=f'Повторяющие значения {self.CHECK_FILED_TAGS}',
                code=400,
            )
        return True

    def check_post_method(self, attrs):
        not_all_fields = len(self.FIELDS) != len(attrs.keys())
        empty_fields = all(
            [bool(attrs['ingredients']), bool(attrs['tags'])]
        )
        if not_all_fields:
            raise ValidationError(
                message='Поле не должно быть пустым',
                code=400
            )
        if not empty_fields:
            raise ValidationError(
                message='Поле не должно быть пустым',
                code=400,
            )
        self.check_tags(attrs)
        return self.check_ingredient(attrs)

    def check_patch_method(self, attrs):
        rule_empty_field_ingredient = 'ingredients' in attrs
        rule_empty_field_tags = 'tags' in attrs
        if not all(
                [rule_empty_field_ingredient, rule_empty_field_tags]
        ):
            raise ValidationError(
                message=f'Пустые поля ингредиент или таги',
                code=400,
            )
        empty_filds = all(
            [bool(attrs['ingredients']), bool(attrs['tags'])]
        )
        if not empty_filds:
            raise ValidationError(
                message=f'Пустые поля ингредиент или таги',
                code=400,
            )
        self.check_tags(attrs)
        return self.check_ingredient(attrs)

    def validate(self, attrs):
        if self.context["request"].method == 'POST':
            return self.check_post_method(attrs)
        return self.check_patch_method(attrs)

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

        recipetags_data = []
        for tag in tags:
            recipetags_data.append(RecipeTag(recipe=model, tag=tag))
        RecipeTag.objects.bulk_create(recipetags_data)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
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

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from foodgram_backend.constant import (
    LENGTH_DISCRIPTION,
    PATH_TO_IMAGES,
    LENGTH_TAG,
    LENGTH_ING_NAME,
    LENGTH_ING_MU,
)
from recipes.core import NameModel, ShopFavorite

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=LENGTH_TAG,
        verbose_name='Название',
        blank=False,
    )

    slug = models.SlugField(
        max_length=LENGTH_TAG,
        unique=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Ingredient(NameModel):
    name = models.CharField(
        max_length=LENGTH_ING_NAME,
        verbose_name='Название',
        blank=False,
    )

    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length=LENGTH_ING_MU,
        blank=False,
    )

    class Meta:
        unique_together = (('name', 'measurement_unit'),)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def clean(self):
        rule_same_ing = Ingredient.objects.filter(
            name=self.name,
            measurement_unit=self.measurement_unit
        )
        if rule_same_ing:
            raise ValidationError("Нельзя подписаться на самого себя.")
        super().clean()


class Recipes(NameModel):
    name = models.CharField(
        max_length=LENGTH_DISCRIPTION,
        verbose_name='Название',
        blank=False,
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        blank=False,

    )
    text = models.TextField(verbose_name='Текст')

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег / Теги',
        related_name='recipes',
    )

    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
        blank=True,
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент / Ингредиенты',
        through='RecipesIngredient',
        related_name='recipes',

    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)],  # Минимальное значение 0
        default=1
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата добавления',
        null=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class RecipesIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        null=True,
        blank=False,
    )

    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        null=True,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        blank=False,
        default=1
    )

    class Meta:
        verbose_name = 'Рецепт и игридиент'
        verbose_name_plural = 'Рецепты и игридиенты'

    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


class ShoppingCart(ShopFavorite):
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        default_related_name = 'shopping_cart'


class FavoriteRecipe(ShopFavorite):
    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite_rec'


class ShortLink(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    short_link = models.CharField(max_length=256, unique=True)
    original_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Коротная ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f"Короткая сылка рецепта {self.recipe.pk}"

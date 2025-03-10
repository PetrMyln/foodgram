from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from foodgram_backend.constant import (
    LENGTH_DISCRIPTION,
    PATH_TO_IMAGES, LENGTH_TAG, LENGTH_ING_NAME, LENGTH_ING_MU
)

User = get_user_model()


class NameModel(models.Model):
    name = models.CharField(
        max_length=LENGTH_DISCRIPTION,
        verbose_name='Название',
        blank=False,
        db_index=True,
        unique=False,
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


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
    DEFAULT_IMAGE = 'default/default.jpg'
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
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']


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
        through='RecipeTag'
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


    def __str__(self):
        return f'{self.recipe} - {self.ingredient}'


    class Meta:
        verbose_name = 'Рецепт и игридиент'
        verbose_name_plural = 'Рецепты и игридиенты'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipes, on_delete=models.CASCADE,
        related_name='tag_recipes',
        null=True,
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE,null=True)

   # class Meta:
 #       unique_together = ('recipe', 'tag')

    class Meta:
        verbose_name = 'Рецепт и тег'
        verbose_name_plural = 'Рецепты и теги'

    def __str__(self):
        return f"{self.recipe.name} - {self.tag.name}"


class ShoppingCart(NameModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
    )
    cooking_time = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        default_related_name ='shopping_cart'


class FavoriteRecipe(NameModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, unique=False)
    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
    )
    cooking_time = models.IntegerField(null=True)

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorite_rec'

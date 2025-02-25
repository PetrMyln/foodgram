from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


from foodgram_backend.constant import (
    LENGTH_DISCRIPTION,
    LENGTH_VALUE,
    PATH_TO_IMAGES, PATH_TO_IMAGES_SHOP,
)


User = get_user_model()


class NameModel(models.Model):
    name = models.CharField(
        max_length=LENGTH_DISCRIPTION,
        verbose_name='Название'
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name




class Tag(NameModel):
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['-id']


class Ingredient(NameModel):

    measurement_unit = models.CharField(
        verbose_name='Еденица измерения',
        max_length= LENGTH_VALUE,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'





class Recipes(NameModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст')

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег / Теги',
        through='RecipeTag',
        related_name='recipes',
    )

    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
    )
    ingredients = models.ManyToManyField(
        'RecipesIngredient',
        verbose_name ='Ингредиент / Ингредиенты',

    )
    cooking_time=models.SmallIntegerField(
        verbose_name ='Время приготовления',
    )


class RecipesIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredient',
        null=True
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.IntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.ingredient.name} {self.amount}'

class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,related_name='tag_recipes')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'tag')

    def __str__(self):
        return f"{self.recipe.name} - {self.tag.name}"


class ShoppingCart(NameModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
    )
    cooking_time =models.IntegerField(null=True)

class FavoriteRecipe(ShoppingCart):
    pass
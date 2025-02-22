from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


from foodgram_backend.constant import (
    LENGTH_DISCRIPTION,
    LENGTH_VALUE,
    PATH_TO_IMAGES,
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




class Teg(NameModel):
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(NameModel):

    value = models.CharField(
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
        verbose_name='Автор публикации',
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        null=True,
        default=timezone.now,
    )
    teg = models.ManyToManyField(Teg, verbose_name='Тег / Теги')
    time_to_prepare = models.SmallIntegerField(
        verbose_name='Время приготовления в минутах',
    )
    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name ='Ингредиент / Ингредиенты',
    )

from django.db import models
from django.contrib.auth import get_user_model

from foodgram_backend.constant import LENGTH_DISCRIPTION, PATH_TO_IMAGES

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


class ShopFavorite(NameModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    recipe = models.ForeignKey("Recipes", on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=PATH_TO_IMAGES,
        verbose_name='Фото',
    )
    cooking_time = models.IntegerField(null=True)

    class Meta:
        abstract = True

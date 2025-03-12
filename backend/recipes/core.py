from django.db import models

from foodgram_backend.constant import LENGTH_DISCRIPTION


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

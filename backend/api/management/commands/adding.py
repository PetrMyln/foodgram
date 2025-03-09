from json import load

from django.core.checks import Tags
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from recipes.models import Ingredient, Tag
from users.models import User

tags = ['111', '222', '333']


class Command(BaseCommand):
    help = 'Add csv files'

    def handle(self, *args, **kwargs):

        with open('./data/ingredients.json') as file:
            rows = load(file)
            for k in rows:
                try:
                    _, _ = Ingredient.objects.get_or_create(
                        name=k['name'],
                        measurement_unit=k['measurement_unit']
                    )
                except Exception:
                    pass
            for tag in tags:
                try:
                    _, _ = Tag.objects.get_or_create(
                        name=tag,
                        slug=tag
                    )
                    print(f'{tag} tags ready')
                except Exception:
                    pass

            try:
                _, _ = User.objects.get_or_create(
                    username='petr',
                    email='1@1.ru',
                    password=make_password('1'),
                    is_staff=True,
                    is_superuser=True
                )
                print('superuser ready')
            except Exception:
                pass

            else:
                print('100% load')

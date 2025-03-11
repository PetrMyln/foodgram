from json import load
from random import choice, randint

from django.core.checks import Tags
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

from recipes.models import Ingredient, Tag, Recipes, RecipesIngredient, RecipeTag
from users.models import User

tags_main = ['111', '222', '333']
users = {
    "email": 'test@1.ru',
    "username": 'TEST',
    "first_name": "Вася",
    "last_name": "Иванов",
    "password": '1'
}


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
            for tag in tags_main:
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
        try:
            value = 1
            value_rec = 1
            for c in range(10):
                print('CCCC')
                user, _ = User.objects.get_or_create(
                    username=str(value) + users.get('username'),
                    email=str(value) + users.get('email'),
                    first_name=str(value) + users.get('first_name'),
                    last_name=str(value) + users.get('last_name'),
                    password=make_password(users.get('password'))
                )
                value += 1

                for x in range(6):
                    tgs_cnt = list(set([choice([1, 2, 3]) for _ in range(3)]))
                    obj, _ = Recipes.objects.get_or_create(
                        name=str(value_rec) + ' ТЕСТОВЫЙ рецепт',
                        author=user,
                        text=str(value_rec) + ' TEST TEXT',
                        cooking_time = value
                    )
                    recipeingredients_data =[]
                    for ingredient in range(2):
                        recipeingredients_data.append(RecipesIngredient(
                            recipe=obj,
                            ingredient=Ingredient.objects.get(pk=randint(1,2000)),
                            amount=value
                        ))
                    RecipesIngredient.objects.bulk_create(recipeingredients_data)
                    recipetags_data = []
                    tags = [(Tag.objects.get(pk=m)) for m in tgs_cnt]
                    for tag in tags:
                        recipetags_data.append(RecipeTag(recipe=obj, tag=tag))
                    RecipeTag.objects.bulk_create(recipetags_data)
                    value_rec+=1
            else:
                print('FINI users, rec')
        except:
            pass

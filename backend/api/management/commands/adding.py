from json import load

from django.core.management.base import BaseCommand

from recipes.models import Ingredient



class Command(BaseCommand):
    help = 'Add csv files'

    def handle(self, *args, **kwargs):

       with open('./data/ingredients.json') as file:
           rows = load(file)
           for k in rows:
               try:
                    _,_=Ingredient.objects.get_or_create(
                        name=k['name'],
                        measurement_unit=k['measurement_unit']
                    )
               except Exception:
                   pass
           else:
               print('100% load')

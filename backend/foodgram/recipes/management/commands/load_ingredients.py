import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):

        with open('../../data/ingredients.json',
                  'r',
                  encoding="utf-8") as file:
            data = json.load(file)
            print('Файл успешно загружен')

            for i in data:
                print('Начало записи в базу...')
                ingredient = Ingredient()
                ingredient.name = i['name']
                ingredient.measurement_unit = i['measurement_unit']
                try:
                    ingredient.save()
                    print(f'{ingredient} записан в базу успешно...')
                except Exception as error:
                    print(f'{error}! {ingredient.name} с единицей измерения '
                          f'{ingredient.measurement_unit} уже есть в базе')
        print('Все данные импортированы успешно!')

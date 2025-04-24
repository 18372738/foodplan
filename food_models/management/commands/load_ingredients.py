import json

from django.core.management.base import BaseCommand
from food_models.models import Ingredient


with open('ingredients.json', 'r') as file:
    DATA = json.load(file)


class Command(BaseCommand):
    help = 'Скачивание ингредиентов через файл'

    def handle(self, *args, **options):
        for ingredient in DATA:
            ingredients, created = Ingredient.objects.update_or_create(
                name=ingredient['name'],
                unit=ingredient['unit'],
                price=ingredient['price']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Добавлен: {ingredients}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлен: {ingredients}"))
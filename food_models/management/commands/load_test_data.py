import json
import random

from django.core.management.base import BaseCommand
from food_models.models import Ingredient, Dish, Recept


with open('ingredients.json', 'r') as file:
    INGREDIENTS = json.load(file)

with open('dishes.json', 'r') as file:
    DISHES = json.load(file)

class Command(BaseCommand):
    help = 'Скачивание тестовых данных'

    def handle(self, *args, **options):
        for ingredient in INGREDIENTS:
            ingredients, created = Ingredient.objects.update_or_create(
                name=ingredient['name'],
                unit=ingredient['unit'],
                price=ingredient['price']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Добавлен: {ingredients}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлен: {ingredients}"))
        for dish in DISHES:
            dishes, created = Dish.objects.update_or_create(
                title=dish['title'],
                img=dish['img'],
                category=dish['category'],
                description=dish['description'],
                instruction=dish['instruction'],
                display_date=29
            )
            for product in dish['ingredients']:
                recepts, cre = Recept.objects.update_or_create(
                    dish=dishes,
                    ingredients=Ingredient.objects.get(name__contains=product),
                    quantity=random.randrange(1, 4)
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Добавлен продукт к блюду: {product}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Обновлен продукт к блюду: {product}"))
            if created:
                self.stdout.write(self.style.SUCCESS(f"Добавлен: {dishes}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлен: {dishes}"))
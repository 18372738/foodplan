import json

from django.core.management.base import BaseCommand
from food_models.models import Dish


with open('dishes.json', 'r') as file:
    DATA = json.load(file)


class Command(BaseCommand):
    help = 'Скачивание блюд через файл'

    def handle(self, *args, **options):
        for dish in DATA:
            dishes, created = Dish.objects.update_or_create(
                title=dish['title'],
                img=dish['img'],
                category=dish['category'],
                description=dish['description']
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Добавлен: {dishes}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Обновлен: {dishes}"))
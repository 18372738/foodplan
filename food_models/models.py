from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from django.db.models.functions import Round


CATEGORIES = [
    ('breakfast', 'Завтрак'),
    ('lunch', 'Обед'),
    ('dinner', 'Ужин'),
    ('dessert', 'Десерт'),
]


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='название',
        max_length=100,
    )
    unit = models.CharField(
        verbose_name='единица измерения',
        max_length=100,
    )
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(
        verbose_name='Имя'
    )
    mail = models.CharField(
        verbose_name='почта',
        max_length=100,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=30,
    )

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return f'{self.name} - {self.mail}'


class Dish(models.Model):
    title = models.CharField(
        verbose_name='название блюда',
        max_length=100
    )
    img = models.ImageField(
        verbose_name='картинка'
    )
    description = models.TextField(
        verbose_name='описание блюда'
    )
    category = models.CharField(
        verbose_name='категория',
        max_length=100,
        choices=CATEGORIES
    )
    instruction = models.TextField(
        verbose_name='рецепт',
        blank=True,
        null=True
        )
    display_date = models.IntegerField(
        verbose_name='дата отображения',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'блюда'

    def get_total_price(self, persons=1):
        total = self.recepts.aggregate(
            total=Round(Sum(F('ingredients__price') * F('quantity')))
        )['total'] or 0
        return total * persons

    def __str__(self):
        return self.title


class Menu(models.Model):
    breakfast = models.ForeignKey(
        Dish,
        verbose_name='завтрак',
        on_delete=models.CASCADE,
        related_name='breakfast_menu'
    )
    lunch = models.ForeignKey(
        Dish,
        verbose_name='обед',
        on_delete=models.CASCADE,
        related_name='lunch_menu'
    )
    dinner = models.ForeignKey(
        Dish,
        verbose_name='ужин',
        on_delete=models.CASCADE,
        related_name='dinner_menu'
    )

    class Meta:
        verbose_name = 'меню'

    def __str__(self):
        return self.id


class Recept(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        related_name='recepts'
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recepts'
    )
    quantity = models.IntegerField(
        verbose_name='количество'
    )

    class Meta:
        verbose_name = 'ингредиент блюда'
        verbose_name_plural = 'ингредиенты блюд'

    def get_total_quantity(self, persons=1):
        return self.quantity * persons

    def __str__(self):
        return self.dish.title


class MealPlanOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    duration_months = models.IntegerField(choices=[(3, '3 мес'), (12, '12 мес')])
    include_breakfast = models.BooleanField()
    include_lunch = models.BooleanField()
    include_dinner = models.BooleanField()
    include_dessert = models.BooleanField()
    new_year_menu = models.BooleanField()
    persons = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def get_selected_meals(self):
        meals = []
        if self.include_breakfast:
            meals.append('Завтрак')
        if self.include_lunch:
            meals.append('Обед')
        if self.include_dinner:
            meals.append('Ужин')
        if self.include_dessert:
            meals.append('Десерт')
        return meals

    def get_count_meals(self):
        count = 0
        if self.include_breakfast:
            count += 1
        if self.include_lunch:
            count += 1
        if self.include_dinner:
            count += 1
        if self.include_dessert:
            count += 1
        return count

    def __str__(self):
        return f'{self.client.name} - {self.created_at}'

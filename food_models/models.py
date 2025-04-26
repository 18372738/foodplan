from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from django.db.models.functions import Round


CATEGORIES = [
    ('breakfast', 'завтраки'),
    ('lunch', 'обеды'),
    ('dinner', 'ужины')
]


class DishQuerySet(models.QuerySet):
    def get_total_price(self):
        total_price = self.annotate(
            price=Round(Sum(
                F('recepts__ingredients__price') * F('recepts__quantity')
                )
            )
        )
        return total_price


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
    objects = DishQuerySet.as_manager()

    class Meta:
        verbose_name_plural = 'блюда'

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

    def __str__(self):
        return self.dish.title


class Order(models.Model):
    client = models.ForeignKey(
        Client,
        verbose_name='клиент',
        on_delete=models.PROTECT,
        related_name='orders'
    )
    address = models.CharField(
        verbose_name='адрес заказа',
        max_length=100,
    )
    total_cost = models.DecimalField(
        verbose_name='общая стоимость',
        max_digits=8,
        decimal_places=2
    )
    registered_at = models.DateTimeField(
        verbose_name='дата регистрации',
        auto_now_add=True,
        db_index=True,
    )
    recept = models.ForeignKey(
        Recept,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.client.name} - {self.address}'


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



class OptionPrice(models.Model):
    OPTION_CHOICES = [
        ('breakfast', 'Завтраки'),
        ('lunch', 'Обеды'),
        ('dinner', 'Ужины'),
        ('dessert', 'Десерты'),
    ]

    option = models.CharField(max_length=20, choices=OPTION_CHOICES, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        verbose_name = 'Цена опции'
        verbose_name_plural = 'Цены опций'

    def __str__(self):
        return f'{self.get_option_display()} — {self.price} ₽'

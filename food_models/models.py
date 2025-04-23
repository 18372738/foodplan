from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User


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
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='client')
    full_name = models.CharField(
        verbose_name='фио'
    )
    mail = models.CharField(
        verbose_name='почта',
        max_length=100,
    )
    phone_number = PhoneNumberField(
        verbose_name='номер клиента'
    )

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return f'{self.full_name} - {self.phone_number}'


class Allergy(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=models.PROTECT,
        related_name='allergy_ingredients',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'аллергичный ингредиент'
        verbose_name_plural = 'аллергичные ингредиенты'

    def __str__(self):
        return self.ingredient.name


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

    class Meta:
        verbose_name = 'блюда'

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
    allergy = models.ForeignKey(
        Allergy,
        on_delete=models.PROTECT,
        related_name='menus'
    )

    class Meta:
        verbose_name = 'меню'

    def __str__(self):
        return self.id


class Recept(models.Model):
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE
    )
    ingredients = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
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
        return f'{self.client.full_name} - {self.address} - {self.client.phone_number}'

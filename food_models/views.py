import random
import uuid

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from yookassa import Configuration, Payment
from food.settings import API_KEY, SHOP_ID

from .forms import MealPlanOrderForm
from .models import Client, MealPlanOrder, Dish


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def order_view(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(id=client_id)

    form = MealPlanOrderForm(request.POST or None)
    total_price = 599 * 3 * 1

    if request.method == 'POST' and form.is_valid():
        order = form.save(commit=False)
        order.client = client
        order.include_breakfast = bool(request.POST.get('select1') == '0')
        order.include_lunch = bool(request.POST.get('select2') == '0')
        order.include_dinner = bool(request.POST.get('select3') == '0')
        order.include_dessert = bool(request.POST.get('select4') == '0')
        order.duration_months = int(request.POST.get('duration_months', 3))
        persons_raw = request.POST.get('persons', 1)
        order.persons = int(persons_raw) + 1
        total_price = calculate_price_from_form(request.POST)
        order.total_cost = total_price
        order.save()
        request.session['order_id'] = order.id

        return redirect('payment', order_id=order.id)

    if request.GET:
        total_price = calculate_price_from_form(request.GET)

    return render(request, 'order.html', {'form': form, 'price': total_price})


def payment(request, order_id=None):
    """Оплата заказа."""
    Configuration.account_id = SHOP_ID
    Configuration.secret_key = API_KEY

    try:
        order = MealPlanOrder.objects.get(id=order_id)
    except MealPlanOrder.DoesNotExist:
        return redirect('order')

    total_price = order.total_cost
    payment = Payment.create({
        "amount": {
            "value": f"{total_price}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "http://127.0.0.1:8000/lk/"
        },
        "capture": True,
        "description": f"Оплата заказа №{order.id} клиента {order.client.name}"
    }, uuid.uuid4())

    return HttpResponseRedirect(payment.confirmation.confirmation_url)


def registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mail = request.POST.get('mail')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        if  password != password_confirm:
            return render(request, 'registration.html', {
                'error': 'Пароли не совпадают'
            })

        if Client.objects.filter(mail=mail).exists():
            return render(request, 'registration.html', {
                'error': 'Пользователь с таким email уже существует. Используйте кнопку войти.'
            })

        hashed_password = make_password(password)
        Client.objects.create(
            name=name,
            mail=mail,
            password=hashed_password
        )
        return redirect('auth')

    return render(request, 'registration.html')


def auth(request):
    if request.method == 'POST':
        mail = request.POST.get('mail')
        password = request.POST.get('password')

        try:
            client = Client.objects.get(mail=mail)
            if check_password(password, client.password):
                request.session['client_id'] = client.id
                return redirect('lk')
            else:
                messages.error(request, "Неверный пароль")
                return redirect('auth')

        except Client.DoesNotExist:
            messages.error(request, "Пользователь с таким email не зарегистрирован")
            return redirect('registration')

    return render(request, 'auth.html')


def lk(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(id=client_id)
    order = MealPlanOrder.objects.filter(client=client).order_by('-created_at').first()
    if order is None:
            return render(request, 'lk.html', {
                'client': client,
                'message': 'У вас нет активных подписок.',
            })
    end_date = order.created_at + relativedelta(months=order.duration_months)
    now = timezone.now()
    if end_date < now:
        return render(request, 'lk.html', {
            'client': client,
            'message': 'Срок действия подписки истёк.',
        })

    today_day = now.day
    dishes = {}
    categories = {
        'Завтрак': 'breakfast',
        'Обед': 'lunch',
        'Ужин': 'dinner',
        'Десерт': 'dessert',
    }

    for category, category_name in categories.items():
        if getattr(order, f"include_{category_name.lower()}"):
            meals = Dish.objects.filter(category=category_name, display_date=today_day)
            for meal in meals:
                meal.total_price = meal.get_total_price() * order.persons

            dishes[category] = {
                'meals': meals,
                'total_quantities': [
                    (recept.ingredients.name, recept.get_total_quantity(order.persons))
                    for meal in meals
                    for recept in meal.recepts.all()
                ]
            }

    context = {
        'client': client,
        'order': order,
        'dishes': dishes,
        'end_date': end_date,
        'count_meals': order.get_count_meals(),
    }

    return render(request, 'lk.html', context)


def update_profile(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(id=client_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password and password != password_confirm:
            return render(request, 'lk.html', {
                'client': client,
                'error': 'Пароли не совпадают'
            })

        client = Client.objects.get(id=client_id)
        client.name = name
        client.mail = email
        if password:
            client.password = make_password(password)
        client.save()
        messages.success(request, 'Изменения успешно сохранены')

        return redirect('lk')

    return redirect('lk')


def get_option_price(option_key):
    return OptionPrice.objects.get(option=option_key).price


def calculate_price_from_form(post_data):
    cost_per_month = 599
    if not post_data:
        duration = 3
        persons = 1
    else:
        duration_raw = post_data.get("duration_months")
        if duration_raw is not None:
            duration = int(duration_raw)
        else:
            duration = 3

        persons_raw = post_data.get("persons")
        if persons_raw is not None:
            persons = int(persons_raw) + 1
        else:
            persons = 1

    total_price = cost_per_month * duration * persons
    return total_price


def calculate_price_api(request):
    if request.method == 'GET':
        total = calculate_price_from_form(request.GET)
        return JsonResponse({'price': float(total)})


def show_random_recipe(request):
    all_dishes = list(Dish.objects.all())
    today = timezone.now().date()
    random.seed(today.toordinal())
    selected_dish = random.choice(all_dishes)
    total_price = selected_dish.get_total_price()

    context = {
        'recept': selected_dish,
        'total_price': total_price
    }

    return render(request, 'recept.html', context)

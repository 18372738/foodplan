import random

from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from .forms import MealPlanOrderForm
from .models import Client, MealPlanOrder, OptionPrice, Dish


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def order_view(request):
    if request.method == 'POST':
        form = MealPlanOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = Client.objects.first()
            total_price = calculate_price_from_form(request.POST)
            order.total_cost = total_price
            order.save()
            form.save_m2m()
            return render(request, 'order.html', {'form': form, 'price': total_price})
    else:
        if request.GET.get("select1") is not None:
            # пользователь что-то выбрал → считаем по GET
            total_price = calculate_price_from_form(request.GET)
            form = MealPlanOrderForm(request.GET)
        else:
            # первый заход → дефолт
            dummy_data = {
                'select1': '0',
                'select2': '0',
                'select3': '0',
                'select4': '0',
                'select5': '0',
                # 'select6': '0',
            }
            total_price = calculate_price_from_form(dummy_data)
            form = MealPlanOrderForm()

    return render(request, 'order.html', {'form': form, 'price': total_price})


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

        Client.objects.create(
            name=name,
            mail=mail,
            password=password
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
    dishes = {}
    categories = {
        'Завтрак': 'breakfast',
        'Обед': 'lunch',
        'Ужин': 'dinner',
        'Десерт': 'dessert',
    }

    for category, category_name in categories.items():
        if getattr(order, f"include_{category_name.lower()}"):
            meals = Dish.objects.filter(category=category_name)
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
    base_price = 0

    def get(option_key):
        try:
            return OptionPrice.objects.get(option=option_key).price
        except OptionPrice.DoesNotExist:
            return 0

    if post_data.get("select1") == "0":
        base_price += get("breakfast")
    if post_data.get("select2") == "0":
        base_price += get("lunch")
    if post_data.get("select3") == "0":
        base_price += get("dinner")
    if post_data.get("select4") == "0":
        base_price += get("dessert")

    persons_raw = post_data.get("select6")
    if persons_raw is not None:
        persons = int(persons_raw) + 1
    else:
        persons = 1

    duration_raw = post_data.get("duration")
    if duration_raw is not None:
        duration = int(duration_raw)
    else:
        duration = 3

    total_price = base_price * persons * duration
    return total_price


def calculate_price_api(request):
    if request.method == 'GET':
        total = calculate_price_from_form(request.GET)
        return JsonResponse({'price': float(total)})


def show_random_recipe(request):
    all_dishes = list(Dish.objects.get_total_price())
    today = timezone.now().date()
    random.seed(today.toordinal())
    selected_dish = random.choice(all_dishes)

    context = {'recept': selected_dish}

    return render(request, 'recept.html', context)

from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse

from .forms import MealPlanOrderForm
from .models import Client, MealPlanOrder, OptionPrice
from .models import Client




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
                'select6': '0',
            }
            total_price = calculate_price_from_form(dummy_data)
            form = MealPlanOrderForm()

    return render(request, 'order.html', {'form': form, 'price': total_price})



def registration(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        mail = request.POST.get('mail')
        password = request.POST.get('password')

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
        try:
            client = Client.objects.get(mail=mail)
            request.session['client_id'] = client.id
            return redirect('lk')
        except Client.DoesNotExist:
            return redirect('registration')

    return render(request, 'auth.html')


def lk(request):
    client_id = request.session.get('client_id')
    client = Client.objects.get(id=client_id)

    return render(request, 'lk.html', {'client': client})


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
            client.password = password
        client.save()

        return redirect('lk')

    return redirect('lk')


def get_option_price(option_key):
    return OptionPrice.objects.get(option=option_key).price

def calculate_price_from_form(post_data):
    base_price = 0

    if post_data.get("select1") == "0":
        base_price += get_option_price("breakfast")
    if post_data.get("select2") == "0":
        base_price += get_option_price("lunch")
    if post_data.get("select3") == "0":
        base_price += get_option_price("dinner")
    if post_data.get("select4") == "0":
        base_price += get_option_price("dessert")
    if post_data.get("select5") == "0":
        base_price += get_option_price("new_year")

    persons = int(post_data.get("select6") or 0) + 1
    duration = int(post_data.get("duration") or 3)
    total_price = base_price * persons * duration

    return total_price


def calculate_price_api(request):
    if request.method == 'GET':
        total = calculate_price_from_form(request.GET)
        return JsonResponse({'price': float(total)})

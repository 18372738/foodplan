from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from .forms import MealPlanOrderForm
from .models import Client, MealPlanOrder

from .models import Client


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def order_view(request):
    if request.method == 'POST':
        form = MealPlanOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = Client.objects.first()  # временно — без request.user
            order.total_cost = 0
            order.save()
            form.save_m2m()
            return redirect('success')
    else:
        form = MealPlanOrderForm()

    return render(request, 'order.html', {'form': form})


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

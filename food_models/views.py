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
        return redirect('lk')

    return render(request, 'registration.html')


def auth(request):
    if request.method == 'POST':
        mail = request.POST.get('mail')
        try:
            client = Client.objects.get(mail=mail)
            return redirect('lk')
        except Client.DoesNotExist:
            return redirect('registration')

    return render(request, 'auth.html')


def lk(request):
    return render(request, 'lk.html')

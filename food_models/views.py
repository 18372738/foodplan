from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from .forms import MealPlanOrderForm
from .models import Client, MealPlanOrder


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
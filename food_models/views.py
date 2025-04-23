from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from .models import Client


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


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

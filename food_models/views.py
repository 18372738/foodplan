from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")

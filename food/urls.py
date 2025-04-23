from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from food_models import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('auth/', views.auth, name='auth'),
    path('lk/', views.lk, name='lk'),
]

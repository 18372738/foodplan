from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from food_models import views
from food_models.views import order_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('order/', order_view, name='order'),
]

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from food_models import views
from food_models.views import order_view, show_random_recipe



urlpatterns = [
    path('admin/', admin.site.urls),
    path('order/', order_view, name='order'),
    path('', views.index, name='index'),
    path('registration/', views.registration, name='registration'),
    path('auth/', views.auth, name='auth'),
    path('lk/', views.lk, name='lk'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('api/calculate-price/', views.calculate_price_api, name='calculate_price_api'),
    path('random_recipe/', show_random_recipe, name='recipe_random'),
    path('payment/', views.payment, name='payment'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

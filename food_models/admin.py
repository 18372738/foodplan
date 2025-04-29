import openpyxl

from django.shortcuts import reverse, redirect
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django import forms
from django.db import models

from .models import Client, Dish, Ingredient, Recept, MealPlanOrder


class ReceptInline(admin.TabularInline):
    model = Recept
    raw_id_fields = ['ingredients']
    extra = 5


class ClientAdminForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(render_value=True),
        required=False
    )

    class Meta:
        model = Client
        fields = '__all__'


class CreatedMonthFilter(admin.SimpleListFilter):
    title = ('Месяц создания')
    parameter_name = 'created_month'

    def lookups(self, request, model_admin):
        months = MealPlanOrder.objects.dates('created_at', 'month')
        return [(date.strftime('%Y-%m'), date.strftime('%B %Y')) for date in months]

    def queryset(self, request, queryset):
        if self.value():
            year, month = map(int, self.value().split('-'))
            return queryset.filter(created_at__year=year, created_at__month=month)
        return queryset


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'mail',)
    form = ClientAdminForm

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.password = make_password(form.cleaned_data['password'])
        obj.save()


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'title',
        'description',
    ]
    list_display_links = [
        'title',
    ]
    fields = [
        'title',
        'description',
        'category',
        'img',
        'get_preview',
        'instruction',
        'display_date'
    ]
    readonly_fields = ['get_preview']
    inlines = [ReceptInline]

    def get_preview(self, obj):
        return format_html(
            '<img src="{0}" style="max-width: {1}; max-height: {1}">',
            obj.img.url,
            '200px',
        )
    get_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.img or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:food_models_dish_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.img.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'price']


def export_to_excel(modeladmin, request, queryset):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Заказы"

    headers = [
        'ID', 'Клиент', 'Месяцы', 'Завтрак', 'Обед', 'Ужин', 'Десерт',
        'Персоны', 'Стоимость', 'Создан'
    ]
    ws.append(headers)

    for order in queryset:
        ws.append([
            order.id,
            str(order.client),
            order.duration_months,
            'Да' if order.include_breakfast else 'Нет',
            'Да' if order.include_lunch else 'Нет',
            'Да' if order.include_dinner else 'Нет',
            'Да' if order.include_dessert else 'Нет',
            order.persons,
            float(order.total_cost),
            order.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=mealplan_orders.xlsx'
    wb.save(response)
    return response
export_to_excel.short_description = "Выгрузить в Excel"


@admin.register(MealPlanOrder)
class MealPlanOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'client',
        'duration_months',
        'include_breakfast',
        'include_lunch',
        'include_dinner',
        'include_dessert',
        'persons',
        'total_cost',
        'created_at',
    )
    list_filter = (CreatedMonthFilter,)
    search_fields = ('id', 'client__name')
    actions = [export_to_excel]

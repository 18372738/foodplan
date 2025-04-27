from django.contrib.auth.hashers import make_password
from django.contrib import admin
from django.utils.html import format_html
from django import forms

from .models import Client, Dish, Ingredient, Recept, MealPlanOrder, OptionPrice


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
        'title',
        'description',
    ]
    fields = [
        'title',
        'description',
        'category',
        'img',
        'get_preview'
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


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit', 'price']


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
    list_filter = ('duration_months', 'include_breakfast', 'include_lunch', 'include_dinner')
    search_fields = ('id', 'client__name')


    from .models import OptionPrice

@admin.register(OptionPrice)
class OptionPriceAdmin(admin.ModelAdmin):
    list_display = ('option', 'price')

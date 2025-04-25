from django.contrib import admin
from django.utils.html import format_html
from django import forms

from .models import Client, Dish, Ingredient, Recept


class ReceptInline(admin.TabularInline):
    model = Recept
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
            obj.password = form.cleaned_data['password']
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

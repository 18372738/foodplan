from django.contrib import admin
from django.utils.html import format_html

from .models import Client, Dish, Ingredient, Recept


class ReceptInline(admin.TabularInline):
    model = Recept
    extra = 5


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'mail',)


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

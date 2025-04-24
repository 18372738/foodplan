from django import forms
from .models import MealPlanOrder, Allergy

class MealPlanOrderForm(forms.ModelForm):
    class Meta:
        model = MealPlanOrder
        fields = [
            'duration_months',
            'include_breakfast',
            'include_lunch',
            'include_dinner',
            'include_dessert',
            'new_year_menu',
            'persons',
            'allergies',
        ]
        widgets = {
            'allergies': forms.CheckboxSelectMultiple()
        }

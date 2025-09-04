from django import forms
from .models import *

class DishForm(forms.ModelForm):
    price = forms.DecimalField(max_digits = 6, decimal_places = 2, min_value = 0.01)
    ingredients = forms.ModelMultipleChoiceField(
        queryset = Ingredient.objects.all(),
        widget = forms.SelectMultiple(attrs = {'size' : '4'}),
        required = True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['img'].label = ""
        self.fields['img'].required = True

    class Meta:
        model = Dish
        fields = ["category", "name", "price", "ingredients", "available", "img"]
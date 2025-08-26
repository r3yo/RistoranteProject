from django import forms
from .models import *

class DishForm(forms.ModelForm):
    ingredients = forms.ModelMultipleChoiceField(
        queryset = Ingredient.objects.all(),
        widget = forms.SelectMultiple(attrs = {'size' : '4'}),
        required = True
    )
    class Meta:
        model = Dish
        fields = ["category", "name", "price", "ingredients", "available", "img"]

class SearchForm(forms.Form):
    name = forms.CharField(label="Name:", required = False)
    category = forms.ModelChoiceField(
        queryset = Category.objects.all(),
        required=False,
        empty_label="Any"
    )
    min_price = forms.DecimalField(label="Minimum price:", required = False)
    max_price = forms.DecimalField(label="Maximum price:", required = False)
    ingredients = forms.ModelMultipleChoiceField(
        queryset = Ingredient.objects.all(),
        required = False,
        widget = forms.SelectMultiple(attrs = {
            'size' : '4'
        }),
        help_text = "Select one or more ingredients to filter dishes"
    )
    available = forms.BooleanField(label="Is available?", required = False)
from django import forms
from .models import *

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ["category", "name", "price", "available"]

class SearchForm(forms.Form):
    name = forms.CharField(label="Name:", required = False)
    category = forms.ModelChoiceField(
        queryset = Category.objects.all(),
        required=False,
        empty_label="Any"
    )
    min_price = forms.DecimalField(label="Minimum price:", required = False)
    max_price = forms.DecimalField(label="Maximum price:", required = False)
    available = forms.BooleanField(label="Is available?", required = False)
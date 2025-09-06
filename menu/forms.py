from django import forms
from .models import *

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']

    def clean_name(self):
        name = re.sub(r"\s+", " ", self.cleaned_data['name']).strip().title()
        if Ingredient.objects.filter(name=name).exists():
            raise forms.ValidationError("An ingredient with this name already exists.")
        
        return name

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
    
    def clean_name(self):
        name = re.sub(r"\s+", " ", self.cleaned_data['name']).strip().title()
        if Ingredient.objects.filter(name=name).exists():
            raise forms.ValidationError("A category with this name already exists.")
        
        return name

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
    
    def clean_name(self):
        name = re.sub(r"\s+", " ", self.cleaned_data['name']).strip().title()
        if Dish.objects.filter(name=name).exists():
            raise forms.ValidationError("A dish with this name already exists.")
        
        return name
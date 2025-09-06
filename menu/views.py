from decimal import Decimal
from django.urls import *
from django.shortcuts import *
from django.views.generic.list import ListView
from django.views.generic.edit import *
from django.views.generic.detail import DetailView
from braces.views import GroupRequiredMixin
from .models import *
from .forms import *

# Create Ingredient
class IngredientCreateView(CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "menu/create_ingredient.html"
    success_url = reverse_lazy('menu:ingredients-list')

# Update Ingredient
class IngredientUpdateView(UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "menu/update_ingredient.html"
    success_url = reverse_lazy('menu:ingredients-list')

    def get_object(self, queryset = None):
        return get_object_or_404(Ingredient, pk = self.kwargs.get("pk"))

# Delete Ingredient
class IngredientDeleteView(DeleteView):
    model = Ingredient
    template_name = "menu/delete_ingredient.html"
    success_url = reverse_lazy('menu:ingredients-list')

    def get_object(self, queryset = None):
        return get_object_or_404(Ingredient, pk = self.kwargs.get("pk"))

class IngredientListView(ListView):
    model = Ingredient
    template_name = "menu/ingredients_list.html"
    context_object_name = "ingredients"
    ordering = ["name"]  # alphabetical

# Create Category
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "menu/create_category.html"
    success_url = reverse_lazy('menu:menu-list')

# Update Category
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "menu/update_category.html"
    success_url = reverse_lazy('menu:menu-list')

    def get_object(self, queryset = None):
        return get_object_or_404(Category, pk = self.kwargs.get("pk"))

# Delete Category
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "menu/delete_category.html"
    success_url = reverse_lazy('menu:menu-list')

    def get_object(self, queryset = None):
        return get_object_or_404(Category, pk = self.kwargs.get("pk"))

class MenuView(ListView):
    model = Category
    template_name = "menu/menu_list.html"
    context_object_name = "categories"

class DishCreateView(GroupRequiredMixin, CreateView):
    group_required = ["Managers"]
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy('menu:menu-list')
    template_name = "menu/create_dish.html"

class DishDetailView(DetailView):
    model = Dish
    form_class = DishForm
    context_object_name = "dish"
    success_url = reverse_lazy('menu:menu-list')
    template_name = "menu/dish_detail.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Dish, pk = self.kwargs.get("pk"))

class DishDeleteView(GroupRequiredMixin, DeleteView):
    group_required = ["Managers"]
    model = Dish
    context_object_name = "dish"
    success_url = reverse_lazy('menu:menu-list')
    template_name = "menu/delete_dish.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Dish, pk = self.kwargs.get("pk"))
    
class DishUpdateView(GroupRequiredMixin, UpdateView):
    group_required = ["Managers"]
    model = Dish
    form_class = DishForm
    context_object_name = "dish"
    success_url = reverse_lazy('menu:menu-list')
    template_name = "menu/update_dish.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Dish, pk = self.kwargs.get("pk"))
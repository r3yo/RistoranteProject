from decimal import Decimal
from django.urls import *
from django.shortcuts import *
from django.views.generic.list import ListView
from django.views.generic.edit import *
from django.views.generic.detail import DetailView
from braces.views import GroupRequiredMixin
from .models import *
from .forms import *
# Create your views here.
class MenuView(ListView):
    model = Category
    template_name = "menu/menu_list.html"
    context_object_name = "categories"

class DishesView(ListView):
    model = Dish
    template_name = "menu/dishes_list.html"
    context_object_name = "dishes"

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
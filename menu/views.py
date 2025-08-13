from django.shortcuts import render
from django.urls import *
from django.shortcuts import *
from django.views.generic.list import ListView
from django.views.generic.edit import *
from django.views.generic.detail import DetailView
from .models import *
from .forms import *

# Create your views here.
class MenuView(ListView):
    model = Category
    template_name = "menu/menu_list.html"
    context_object_name = "categories"
    #def get_queryset(self):
    #    filter_map = {
    #        "min_price" : "price__gte",
    #        "max_price" : "price__lte",
    #        "is_available" : "available",
    #    }

    #    dish_qs = Dish.objects.all()
    #    filters = {}

    #    for param, lookup in filter_map.items():
    #        value = self.request.GET.get(param)
    #        if value is not None:
    #            if value in ["0", "1"]:
    #                value = value == "1"
    #            filters[lookup] = value
        
    #    if filters:
    #        dish_qs = dish_qs.filter(**filters)
        
    #    return Category.objects.filter(dishes__in=dish_qs).distinct()

class DishCreateView(CreateView):
    model = Dish
    form_class = DishForm
    template_name = "menu/create_dish.html"
    success_url = reverse_lazy("menu:menu-list")

class DishDetailView(DetailView):
    template_name = "menu/dish_detail.html"
    context_object_name = "dish"
    def get_object(self, queryset = None):
        return get_object_or_404(Dish, pk=self.kwargs.get("pk"))

class DishDeleteView(DeleteView):
    template_name = "menu/delete_dish.html"
    context_object_name = "dish"
    success_url = reverse_lazy("menu:menu-list")
    def get_object(self, queryset = None):
        return get_object_or_404(Dish, pk=self.kwargs.get("pk"))

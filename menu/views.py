from django.shortcuts import render
from django.views.generic.list import ListView
from .models import *

# Create your views here.
class MenuView(ListView):
    model = Category
    template_name = "menu/menu_list.html"
    context_object_name = "categories"
    def get_queryset(self):
        filter_map = {
            "min_price" : "price__gte",
            "max_price" : "price__lte",
            "is_available" : "available",
        }

        dish_qs = Dish.objects.all()
        filters = {}

        for param, lookup in filter_map.items():
            value = self.request.GET.get(param)
            if value is not None:
                if value in ["0", "1"]:
                    value = value == "1"
                filters[lookup] = value
        
        if filters:
            dish_qs = dish_qs.filter(**filters)
        
        return Category.objects.filter(dishes__in=dish_qs).distinct()
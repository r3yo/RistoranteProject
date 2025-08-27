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
    
def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            for k, v in cleaned.items():
                if hasattr(v, "pk"):
                    cleaned[k] = str(v.pk)
            if 'min_price' in cleaned and cleaned["min_price"] != None:
                cleaned['min_price'] = str(cleaned["min_price"])
            if 'max_price' in cleaned and cleaned["max_price"] != None:
                cleaned['max_price'] = str(cleaned["max_price"])
            cleaned['ingredients'] = [ing.slug for ing in cleaned['ingredients']]
            request.session['field_data'] = cleaned
            return redirect('menu:search-results')
    else:
        form = SearchForm()
    
    return render(request, template_name="menu/search.html", context={"form" : form})

class DishSearchView(DishesView):
    def get_queryset(self):
        query_set = super().get_queryset()
        filter_data = self.request.session.get('field_data', {})
        params = {
            "name" : "name__icontains",
            "category" : "category",
            "min_price" : "price__gte",
            "max_price" : "price__lte",
            "available" : "available",
        }
        filters = {}
        # if available remains unchecked it displays every item, regardless of its availability
        for k, v in params.items():
            if k in filter_data and filter_data[k]:
                if k == 'min_price' or k == 'max_price':
                    filter_data[k] = Decimal(filter_data[k])
                filters[v] = filter_data[k]
        query_set = query_set.filter(**filters)
        ingredients = filter_data['ingredients']
        if ingredients:
            for ing in ingredients:
                query_set = query_set.filter(ingredients = ing)
        return query_set
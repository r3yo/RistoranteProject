from decimal import Decimal
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

class DishesView(ListView):
    model = Dish
    template_name = "menu/dishes_list.html"
    context_object_name = "dishes"
#    def get_queryset(self):
#        self.category = get_object_or_404(Category, slug = self.kwargs["slug"])
#        return Dish.objects.filter(category = self.category)
#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context["category"] = self.category
#        return context

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
    
class DishUpdateView(UpdateView):
    template_name = "menu/update_dish.html"
    context_object_name = "dish"
    form_class = DishForm
    success_url = reverse_lazy("menu:menu-list")
    def get_object(self, queryset = None):
        return get_object_or_404(Dish, pk=self.kwargs.get("pk"))
    
def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data.copy()
            if 'min_price' in cleaned and cleaned["min_price"] != None:
                cleaned['min_price'] = str(cleaned["min_price"])
            if 'max_price' in cleaned and cleaned["max_price"] != None:
                cleaned['max_price'] = str(cleaned["max_price"])
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
            "category" : "category__iexact",
            "min_price" : "price__gte",
            "max_price" : "price__lte",
            "available" : "available",
        }
        filters = {}
        print(filter_data)
        for k, v in params.items():
            if k in filter_data and filter_data[k]:
                if k == 'min_price' or k == 'max_price':
                    filter_data[k] = Decimal(filter_data[k])
                filters[v] = filter_data[k]
        query_set = query_set.filter(**filters)
        return query_set

    #    results = Dish.objects.all()
    #    filters = {
    #        "price__gte" : self.request.resolver_match.kwargs["min_price"],
    #        "price__lte" : self.request.resolver_match.kwargs["max_price"],
    #        "available" : self.request.resolver_match.kwargs["available"],
    #    }
    #    if self.request.resolver_match.kwargs["name"] != "Any":
    #        filters["name__icontains"] = self.request.resolver_match.kwargs["name"]

    #    if self.request.resolver_match.kwargs["category"] != "Any":
    #        filters["category"] = self.request.resolver_match.kwargs["category"]
    #    params = {
    #        "name" : "name__icontains",
    #        "category" : "category__iexact",
    #        "min_price" : "price__gte",
    #        "max_price" : "price__lte",
    #        "available" : "available",
    #    }
    #    filters = {}
    #    for k, v in params.items():
    #        if self.request.resolver_match.kwargs

        
    #    results = results.filter(**filters)
        
    #    return results
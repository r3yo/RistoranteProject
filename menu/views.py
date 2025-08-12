from django.shortcuts import render
from django.views.generic.list import ListView
from .models import *

# Create your views here.
def menu_list(request):
    categories = Category.objects.prefetch_related("items").all()
    templ = "menu/menu_list.html"
    ctx = {"categories" : categories}
    return render(request, template_name=templ, context=ctx)
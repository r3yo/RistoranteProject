from django.shortcuts import render
from django.contrib.auth.forms import *
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy

def home(request):
    return render(request, template_name="extended.html")

class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "create_user.html"
    success_url = reverse_lazy("login")
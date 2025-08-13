from django.urls import path
from . import views

app_name = 'menu'
urlpatterns = [
    path('', views.MenuView.as_view(), name="menu_list"),
]
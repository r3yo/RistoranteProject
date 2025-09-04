from django.urls import path
from . import views
from .views import *

app_name = 'menu'
urlpatterns = [
    path('', MenuView.as_view(), name="menu-list"),
    path('add', DishCreateView.as_view(), name="add-dish"),
    path('<slug:pk>', DishDetailView.as_view(), name="dish-detail"),
    path('<slug:pk>/delete', DishDeleteView.as_view(), name="delete-dish"),
    path('<slug:pk>/update', DishUpdateView.as_view(), name="update-dish")
]
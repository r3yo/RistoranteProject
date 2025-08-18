from django.urls import path
from . import views
from .views import *

app_name = 'menu'
urlpatterns = [
    path('', MenuView.as_view(), name="menu-list"),
    path('add', DishCreateView.as_view(), name="create-dish"),
    path('dish/<int:pk>', DishDetailView.as_view(), name="dish-detail"),
    path('dish/delete/<int:pk>', DishDeleteView.as_view(), name="delete-dish"),
    path('dish/update/<int:pk>', DishUpdateView.as_view(), name="update-dish"),
    path('search', search, name="search"),
    path('search/results', DishSearchView.as_view(), name="search-results")
]
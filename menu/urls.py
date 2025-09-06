from django.urls import path
from . import views
from .views import *

app_name = 'menu'
urlpatterns = [
    path('', MenuView.as_view(), name="menu-list"),
    path('ingredients', IngredientListView.as_view(), name='ingredients-list'),
    path('ingredients/add', IngredientCreateView.as_view(), name='add-ingredient'),
    path('ingredients/<slug:pk>/update', IngredientUpdateView.as_view(), name='update-ingredient'),
    path('ingredients/<slug:pk>/delete', IngredientDeleteView.as_view(), name='delete-ingredient'),
    path("categories/add", views.CategoryCreateView.as_view(), name="add-category"),
    path("categories/<slug:pk>/update", views.CategoryUpdateView.as_view(), name="update-category"),
    path("categories/<slug:pk>/delete", views.CategoryDeleteView.as_view(), name="delete-category"),
    path('add', DishCreateView.as_view(), name="add-dish"),
    path('<slug:pk>', DishDetailView.as_view(), name="dish-detail"),
    path('<slug:pk>/delete', DishDeleteView.as_view(), name="delete-dish"),
    path('<slug:pk>/update', DishUpdateView.as_view(), name="update-dish")
]
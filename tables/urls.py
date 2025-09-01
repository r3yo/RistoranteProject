from django.urls import path
from . import views
from .views import *

app_name = 'tables'
urlpatterns = [
    path('', TableView.as_view(), name = "tables-list"),
    path('add', CreateTableView.as_view(), name = "add-table"),
    path('<slug:pk>', TableDetailView.as_view(), name = "table-detail"),
    path('<slug:pk>/update', UpdateTableView.as_view(), name = "update-table"),
    path('<slug:pk>/delete', DeleteTableView.as_view(), name = "delete-table")
]
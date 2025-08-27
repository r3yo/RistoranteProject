from django.urls import path
from . import views
from .views import *

app_name = 'tables'
urlpatterns = [
    path('', TableView.as_view(), name="tables-list"),
    path('add', CreateTableView.as_view(), name = "add-table"),
    path('<slug:pk>', TableDetailView.as_view(), name = "table-detail"),
    path('update/<slug:pk>', UpdateTableView.as_view(), name = "update-table"),
    path('delete/<slug:pk>', DeleteTableView.as_view(), name = "delete-table"),
    path("reservation/", views.ReservationCreateView.as_view(), name="make-reservation"),
    path('reservation/cancel/<slug:pk>', views.cancel_reservation, name="cancel_reservation"),
    path('reservation/availability_check', views.availability_check, name = "availability-check"),
    path('reservation/availability_check/results', views.AvailabilitySearchView.as_view(), name = "table-availability")
]
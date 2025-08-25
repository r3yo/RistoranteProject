from django.urls import path
from . import views
from .views import *

app_name = 'tables'
urlpatterns = [
    path('', TableView.as_view(), name="tables-list"),
    path("reservation/", views.ReservationCreateView.as_view(), name="make-reservation"),
    path("reservation/cancel/<slug:pk>", views.cancel_reservation, name="cancel_reservation"),
    path('reservation/availability_check', views.availability_check, name = "availability-check"),
    path('reservation/availability_check/results', views.AvailabilitySearchView.as_view(), name = "table-availability")
]
from django.urls import path
from . import views
from .views import *

app_name = 'tables'
urlpatterns = [
    path('', TableView.as_view(), name="tables-list"),
    path("reservation/", views.ReservationCreateView.as_view(), name="make_reservation"),
    path("cancel/<slug:pk>/", views.cancel_reservation, name="cancel_reservation"),
]
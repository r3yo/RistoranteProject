from django.urls import path
from . import views
from .views import *

app_name = 'reservations'

urlpatterns = [
    path('', ReservationListView.as_view(), name = "user-reservations"),
    path('history', ReservationHistoryView.as_view(), name = "reservations-history"),
    path('make', views.ReservationCreateView.as_view(), name = "make-reservation"),
    path('<slug:pk>/cancel', views.cancel_reservation, name = "cancel-reservation"),
    path('<slug:pk>/update', views.update_reservation, name = "update-reservation"),
    path('availability_check', views.availability_check, name = "availability-check"),
    path('availability_check/results', views.AvailabilitySearchView.as_view(), name = "table-availability")
]
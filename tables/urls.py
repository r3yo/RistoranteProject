from django.urls import path
from . import views
from .views import *

app_name = 'tables'
urlpatterns = [
    path('', TableView.as_view(), name = "tables-list"),
    path('my-reservations', ReservationListView.as_view(), name = "user-reservations"),
    path('my-reservations/history', ReservationHistoryView.as_view(), name = "reservations-history"),
    path('reservation', views.ReservationCreateView.as_view(), name="make-reservation"),
    path('add', CreateTableView.as_view(), name = "add-table"),
    path('<slug:pk>', TableDetailView.as_view(), name = "table-detail"),
    path('<slug:pk>/update', UpdateTableView.as_view(), name = "update-table"),
    path('<slug:pk>/delete', DeleteTableView.as_view(), name = "delete-table"),
    path('reservation', views.ReservationCreateView.as_view(), name = "make-reservation"),
    path('reservation/<slug:pk>/cancel', views.cancel_reservation, name = "cancel-reservation"),
    path('reservation/<slug:pk>/update', views.update_reservation, name = "update-reservation"),
    path('reservation/availability_check', views.availability_check, name = "availability-check"),
    path('reservation/availability_check/results', views.AvailabilitySearchView.as_view(), name = "table-availability")
]
from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # Optional JSON endpoint to fetch notifications via AJAX
    path('json/', views.notifications_json, name = 'json'),
    
    # Optional endpoint to mark notifications as read
    path('mark-read/', views.mark_all_read, name = 'mark_all_read'),
]
from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    # JSON endpoint to fetch notifications via AJAX
    path('json/', views.notifications_json, name = 'json'),
    
    # Endpoint to mark notifications as read
    path('mark-read/', views.mark_all_read, name = 'mark_all_read'),
]
# notifications/context_processors.py
from .models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        # Safe access to related notifications
        return {"notifications": Notification.objects.filter(user = request.user, read = False).order_by("-created_at")}
    return {"notifications": []}
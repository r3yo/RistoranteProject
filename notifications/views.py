from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from .models import Notification

@login_required
@never_cache # Prevents browser from caching the return value, always fetches fresh data
def notifications_json(request):
    # Return last 10 notifications
    notifications = Notification.objects.filter(user = request.user, read = False).order_by('-created_at')[:10]
    data = [
        {"id": n.id, "message": n.message, "type": n.get_type_display(), "read": n.read, "created_at": n.created_at.strftime("%H:%M %d-%m-%Y")}
        for n in notifications
    ]
    return JsonResponse(data, safe = False) # safe = False is necessary because data is a list not a dict, this way data can be accepted

@login_required
def mark_all_read(request):
    Notification.objects.filter(user = request.user, read = False).update(read = True)
    return JsonResponse({'status': 'ok'})
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notifications_json(request):
    # Return last 10 notifications
    notifications = Notification.objects.filter(user = request.user).order_by('-created_at')[:10]
    data = [
        {"id": n.id, "message": n.message, "type": n.type, "read": n.read, "created_at": n.created_at.strftime("%H:%M %d-%m-%Y")}
        for n in notifications
    ]
    return JsonResponse(data, safe=False)

@login_required
def mark_all_read(request):
    Notification.objects.filter(user = request.user, read = False).update(read = True)
    return JsonResponse({'status': 'ok'})

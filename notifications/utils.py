from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.core.mail import send_mail

def send_notification(user, message, notif_type = 'CONFIRM', send_email = True):
    # Save in DB
    Notification.objects.create(user = user, message = message, type = notif_type)

    # Send via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {"type": "send_notification", "message": {"message": message, "type": notif_type}}
    )

    # Optional email
    if send_email:
        send_mail(
            subject = f"Notification: {notif_type}",
            message = message,
            from_email = "noreply@restaurant.com",
            recipient_list = [user.email],
            fail_silently = True,
        )
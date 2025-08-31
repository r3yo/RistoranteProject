from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.core.mail import send_mail

def send_notification(user, message, notif_type):
    # Save in DB
    Notification.objects.create(user = user, message = message, type = notif_type)

    # Send via WebSocket and dispatch message as an event of type "send_notification"
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {"type": "send_notification", "message": {"message": message, "type": notif_type}}
    )
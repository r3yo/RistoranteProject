from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from threading import Timer
from reservations.models import Reservation, WaitlistEntry
from notifications.models import Notification

def cleanup_expired_reservations():
    today = timezone.localdate()
    delta = today - timedelta(days=30)  # approximate 1 month

    expired_res = Reservation.objects.filter(date__lt=delta)
    count = expired_res.count()
    expired_res.delete()
    print(f"Deleted {count} expired reservations")

def cleanup_expired_waitlist_entries():
    expired_entries = WaitlistEntry.objects.filter(
        Q(date__lt=timezone.localdate()) | Q(date=timezone.localdate(), start_hour__lt=timezone.localtime())
    )
    
    count = expired_entries.count()
    expired_entries.delete()
    print(f"Deleted {count} expired waitlist entries (hourly)")

def cleanup_notifications():
    read_notifs = Notification.objects.filter(read=True)
    count = read_notifs.count()
    read_notifs.delete()
    print(f"Deleted {count} read notifications")

def start_periodic_cleanup(interval_seconds=3600): #every hour
    # Run cleanup functions
    cleanup_expired_reservations()
    cleanup_notifications()
    cleanup_expired_waitlist_entries()
    
    # Schedule the next run
    Timer(interval_seconds, start_periodic_cleanup, [interval_seconds]).start()
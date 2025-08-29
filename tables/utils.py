from .models import Reservation, Table

def get_conflicting_reservations(table, date, start_hour, end_hour):
    """
    Returns True if the table is free for the given date and time slot,
    False if there is a conflicting reservation.
    """
    return Reservation.objects.filter(
        table = table,
        date = date,
        start_hour__lt = end_hour,
        end_hour__gt = start_hour
    )
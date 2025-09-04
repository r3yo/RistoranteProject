from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import *
from django.views.generic import *
from django.shortcuts import *
from django.urls import *
from datetime import *
from django.contrib.auth.mixins import *
from django.contrib.auth.decorators import *
from notifications.utils import send_notification
from reservations.utils import get_conflicting_reservations
from tables.models import Table
from .models import *
from .forms import *
# Create your views here.

def add_to_waitlist(user, date, start_hour, end_hour, guests):
    """
    Create a waitlist entry if it doesn't already exist.
    Returns True if created, False if it already existed.
    """

    try:
        WaitlistEntry.objects.create(
            user = user,
            date = date,
            start_hour = start_hour,
            end_hour = end_hour,
            guests = guests
        )
        return True
    except IntegrityError:
        return False

def notify_waitlist(table, date, start_hour, end_hour):
    """
    Notify all users on the waitlist if a table becomes available
    for the specified date, time, and number of guests.
    """
    waitlist_entries = WaitlistEntry.objects.filter(
        date = date,
        start_hour__gte = start_hour,
        end_hour__lte = end_hour,
        guests = table.seats
    )

    for entry in waitlist_entries:
        # Check conflicts only for this table
        conflict = get_conflicting_reservations(table, entry.date, entry.start_hour, entry.end_hour).exists()

        if not conflict:
            # Notify user
            send_notification(
                user = entry.user,
                message = f"Table available on {entry.date} at {entry.start_hour}-{entry.end_hour}",
                notif_type = 'UPDATE'
            )

            # Remove from waitlist
            entry.delete()

def send_reminders(user):
    """
    Send out reminders to the logged in user
    """
    for r in Reservation.objects.filter(user = user, date = timezone.localdate(), start_hour__gte = timezone.localtime()):
        send_notification(
            user = user,
            message = f"Today you have a reservation for {r.guests} from {r.start_hour} to {r.end_hour}.",
            notif_type = 'REMINDER'
        )

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/make_reservation.html'
    login_url = '/login-or-register/'

    def get_form_class(self):
        if self.request.user.groups.filter(name = "Managers").exists() or self.request.user.is_staff:
            return ManagerReservationForm
        return ReservationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user # pass user into the form constructor
        
        return kwargs

    def form_valid(self, form):
        table = form.cleaned_data["table"]
        join_waitlist = form.cleaned_data["join_waitlist"]
        
        if self.request.user.groups.filter(name = "Managers").exists() or self.request.user.is_superuser:
            user = form.cleaned_data["user"]
        else:
            user = self.request.user

        if table:
            # Table available --> save reservation
            self.object = form.save()
            messages.success(self.request, "Reservation created successfully.")
            send_notification(
                user = user,
                message = f"Reservation created successfully for {form.cleaned_data["guests"]} on {form.cleaned_data["date"]} at {dict(Table.HOURS_CHOICES).get(int(form.cleaned_data["time"][0]))}.",
                notif_type = 'CONFIRM'
            )
        
        elif join_waitlist:
            # No table --> add to waitlist
            added = add_to_waitlist(
                user,
                form.cleaned_data["date"],
                form.cleaned_data["start_hour"],
                form.cleaned_data["end_hour"],
                form.cleaned_data["guests"]
            )
            if added:
                messages.success(self.request, "No table available. You've been added to the waitlist.")
            else:
                messages.error(self.request, "You have already been added to this waitlist.")
            
            return redirect("home")

        else:
            # No table and user didn't join waitlist
            messages.warning(self.request, "No table available and you did not join the waitlist.")
            return self.form_invalid(form)
        
        return super().form_valid(form)
        
    def get_success_url(self):
        # If the reservation user is the same as the logged-in user
        if self.object.user == self.request.user:
            return reverse_lazy("reservations:user-reservations")
        else:
            return reverse_lazy("tables:tables-list")

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "reservations/user_reservations.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(
            user = self.request.user,
            date__gte = timezone.localdate()
        ).order_by("date", "start_hour")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "My Active Reservations",
            "heading": "My Active Reservations",
            "reservations": context['reservations'],
            "actions": [
                {"url_name": "reservations:update-reservation", "label": "Edit", "class": "btn-primary mr-1"},
                {"url_name": "reservations:cancel-reservation", "label": "Cancel", "class": "btn-danger"},
            ],
            "empty_message": "You have no reservations."
        })
        return context

class ReservationHistoryView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "reservations/reservations_history.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(
            user = self.request.user
        ).filter(
            models.Q(date__lt = timezone.localdate()) |
            models.Q(date = timezone.localdate(), start_hour__lt = timezone.localtime())
        ).order_by("-date", "-start_hour")[:10]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "title": "Reservation History",
            "heading": "Reservation History",
            "reservations": context['reservations'],
            "actions": None,  # No buttons for history
            "empty_message": "You have no past reservations."
        })
        return context

# Check function for reservation update/cancellation permission
def is_user_authorized(request, reservation):
    return reservation.user == request.user or request.user.groups.filter(name = "Managers").exists() or request.user.is_superuser

def redirect_after_reservation(reservation, user):
    """
    Redirects based on whether the reservation belongs to the current user.
    - If the reservation is for the user → redirect to user's reservations
    - Otherwise → redirect to the table detail page
    """
    if reservation.user == user:
        return redirect("reservations:user-reservations")
    
    elif user.groups.filter(name = "Managers").exists() or user.is_superuser:
        return redirect("tables:table-detail", pk = reservation.table.slug)
    
    else:
        return redirect("home")

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, slug = pk)

    if not is_user_authorized(request, reservation):
        messages.error(request, "You don't have permissions to delete this reservation.")
        
        return redirect_after_reservation(reservation, request.user)

    if request.method == "POST":
        # Delete the reservation and redirect
        reservation.delete()
        notify_waitlist(reservation.table, reservation.date, reservation.start_hour, reservation.end_hour)
        return redirect_after_reservation(reservation, request.user)

    return render(request, "reservations/cancel_reservation.html", {"reservation" : reservation})

@login_required
def update_reservation(request, pk):
    reservation = get_object_or_404(Reservation, slug = pk)

    if not is_user_authorized(request, reservation):
        messages.error(request, "You don't have permissions to update this reservation.")
        
        return redirect_after_reservation(reservation, request.user)

    if request.method == "POST":
        form = ReservationForm(request.POST, instance = reservation, user = request.user)

        if form.is_valid():
            old_table = reservation.table
            old_start = reservation.start_hour
            old_end = reservation.end_hour
            old_date = reservation.date

            if form.cleaned_data.get("table"):
                # Table is available --> notify waitlist first
                
                form.save()

                notify_waitlist(old_table, old_date, old_start, old_end)
                messages.success(request, "Reservation updated successfully.")

            elif form.cleaned_data.get("join_waitlist"):
                # No table --> add to waitlist only
                added = add_to_waitlist(
                    request.user,
                    form.cleaned_data["date"],
                    form.cleaned_data["start_hour"],
                    form.cleaned_data["end_hour"],
                    form.cleaned_data["guests"]
                )
                if added:
                    messages.success(request, "No table available. You've been added to the waitlist.")
                else:
                    messages.warning(request, "You have already been added to this waitlist.")

            else:
                # No table and user didn't join waitlist
                messages.error(request, "No table available and you did not join the waitlist.")

            return redirect_after_reservation(reservation, request.user)

        else:
            return redirect_after_reservation(reservation, request.user)

    else:
        time_slot = list(range(reservation.start_hour.hour, reservation.end_hour.hour)) 
        form = ReservationForm(instance = reservation, user = request.user, initial = {'time' : time_slot})

    return render(request, "reservations/update_reservation.html", {"form": form})

def availability_check(request):
    if request.method == "POST":
        form = AvailabilityCheckForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            request.session['field_data'] = {
                'date' : str(cleaned['date']),
                'guests' : str(cleaned['guests']),
                'requested_hours' : cleaned['time'] 
            }
            return redirect('reservations:table-availability')
    else:
        form = AvailabilityCheckForm()

    return render(request, template_name = "reservations/table_availability_search.html", context = {"form" : form})

class AvailabilitySearchView(ListView):
    model = Table
    template_name = "reservations/availability_list.html"
    context_object_name = "tables"

    def get_queryset(self):
        query_set = super().get_queryset()
        form_data = self.request.session.get('field_data', {})
        guests = form_data.get("guests")
        if guests != "None":
            guests = int(form_data.get('guests'))
            query_set = query_set.filter(seats = guests)
        return query_set
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_data = self.request.session.get('field_data', {})
        date = datetime.strptime(form_data.get("date"), "%Y-%m-%d").date()
        requested_hours = form_data.get("requested_hours") # list of selected hours or None
        
        if requested_hours:
            requested_hours_int = [int(h) for h in requested_hours]

        tables_with_availability = []

        for table in context["tables"]:
            reserved = table.reservations.filter(date = date)
            available_hours = [(h, label) for h, label in table.HOURS_CHOICES]

            for r in reserved:
                start = r.start_hour.hour
                end = r.end_hour.hour
                occupied_hours = range(start, end) # Occupied hours for reservation
                available_hours = [(h, label) for h, label in available_hours if h not in occupied_hours]

            if requested_hours:
                available_hours = [(h, label) for h, label in available_hours if h in requested_hours_int]
            
            if available_hours:
                tables_with_availability.append({
                    "table": table,
                    "hours": available_hours
                })

        context['tables_with_availability'] = tables_with_availability

        return context
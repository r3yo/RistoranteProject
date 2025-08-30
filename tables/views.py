from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.shortcuts import *
from django.views.generic import *
from django.shortcuts import *
from django.urls import *
from datetime import *
from django.contrib.auth.mixins import *
from django.contrib.auth.decorators import *
from braces.views import GroupRequiredMixin
from notifications.utils import send_notification
from .models import *
from .forms import *
# Create your views here.

class CreateTableView(GroupRequiredMixin, CreateView):
    group_required = ["Managers"]
    model = Table
    form_class = TableForm
    success_url = reverse_lazy('tables:tables-list')
    template_name = "tables/create_table.html"

class UpdateTableView(GroupRequiredMixin, UpdateView):
    group_required = ["Managers"]
    model = Table
    form_class = TableForm
    context_object_name = "table"
    success_url = reverse_lazy('tables:tables-list')
    template_name = "tables/update_table.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Table, pk = self.kwargs.get("pk"))

class DeleteTableView(GroupRequiredMixin, DeleteView):
    group_required = ["Managers"]
    model = Table
    context_object_name = "table"
    success_url = reverse_lazy('tables:tables-list')
    template_name = "tables/delete_table.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Table, pk = self.kwargs.get("pk"))

class TableView(GroupRequiredMixin, ListView):
    group_required = ["Managers"]
    model = Table
    template_name = "tables/tables_list.html"
    context_object_name = "tables"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Add active reservations for each table, updates automatically
        for table in context['tables']:
            table.active_reservations = table.reservations.filter(
                date__gte = timezone.localdate()
            ).order_by("date", "start_hour")
        
        return context

class TableDetailView(GroupRequiredMixin, DetailView):
    group_required = ["Managers"]
    model = Table
    context_object_name = "table"
    success_url = reverse_lazy('tables:tables-list')
    template_name = "tables/table_detail.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Table, pk = self.kwargs.get("pk"))

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
                message = f"Tavolo disponibile il {entry.date} {entry.start_hour}-{entry.end_hour}",
                notif_type = 'UPDATE'
            )

            # Remove from waitlist
            entry.delete()

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'tables/make_reservation.html'
    login_url = '/login-or-register/'
    success_url = reverse_lazy('tables:user-reservations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user      # pass user into the form constructor
        return kwargs

    def form_valid(self, form):
        table = form.cleaned_data["table"]
        join_waitlist = form.cleaned_data["join_waitlist"]

        if table:
            # Table available → save reservation
            form.save()
            messages.success(self.request, "Reservation created successfully.")
            return super().form_valid(form)
        
        elif join_waitlist:
            # No table → add to waitlist
            added = add_to_waitlist(
                self.request.user,
                form.cleaned_data["date"],
                form.cleaned_data["start_hour"],
                form.cleaned_data["end_hour"],
                form.cleaned_data["guests"]
            )
            if added:
                messages.success(self.request, "No table available. You've been added to the waitlist.")
            else:
                messages.warning(self.request, "You have already been added to this waitlist.")
        
            return redirect(self.success_url)
        else:
            # No table and user didn't join waitlist
            form.add_error(None, "No table available and you did not join the waitlist.")
            return self.form_invalid(form)
        
    def form_invalid(self, form):
    # Called if form.is_valid() fails
        for field, errors in form.errors.items():
            for error in errors:
                if field == "__all__":
                    messages.error(self.request, error)
                else:
                    messages.error(self.request, f"{field}: {error}")

        return super().form_invalid(form)

class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "tables/user_reservations.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(
            user = self.request.user,
            date__gte = timezone.localdate()
        ).order_by("date", "start_hour")

class ReservationHistoryView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = "tables/reservations_history.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(
            user = self.request.user
        ).filter(
            models.Q(date__lt = timezone.localdate()) |
            models.Q(date = timezone.localdate(), start_hour__lt = timezone.localtime())
        ).order_by("-date", "-start_hour")

# Check function for reservation update/cancellation permission
def is_user_authorized(request, reservation):
    return reservation.user == request.user or request.user.groups.filter(name = "Managers").exists()

@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, slug = pk)

    if not is_user_authorized(request, reservation):
        return HttpResponseForbidden("You don't have permission to cancel this reservation.")

    if request.method == "POST":
        # Delete the reservation and redirect
        reservation.delete()
        notify_waitlist(reservation.table, reservation.date, reservation.start_hour, reservation.end_hour)
        return redirect("tables:user-reservations")

    return render(request, "tables/cancel_reservation.html", {"reservation" : reservation})

@login_required
def update_reservation(request, pk):
    reservation = get_object_or_404(Reservation, slug = pk)

    if not is_user_authorized(request, reservation):
        return HttpResponseForbidden("You don't have permission to update this reservation.")

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

            return redirect('tables:user-reservations')

        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    if field == "__all__":
                        messages.error(request, error)
                    else:
                        messages.error(request, f"{field}: {error}")

    else:
        form = ReservationForm(instance = reservation, user = request.user)

    return render(request, "tables/update_reservation.html", {"form": form})

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
            return redirect('tables:table-availability')
    else:
        form = AvailabilityCheckForm()

    return render(request, template_name="tables/table_availability_search.html", context={"form" : form})

class AvailabilitySearchView(TableView):
    template_name = "tables/availability_list.html"

    def get_queryset(self):
        query_set = super().get_queryset()
        form_data = self.request.session.get('field_data', {})
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

        tables_with_availability = {table.number : [] for table in context['tables']}

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
     
            tables_with_availability[table.number] = available_hours

        context['availability'] = tables_with_availability
        return context
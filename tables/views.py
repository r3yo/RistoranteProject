from django.shortcuts import *
from django.views.generic import *
from django.shortcuts import *
from django.urls import *
from datetime import *

from .models import *
from .forms import *
# Create your views here.

class TableView(ListView):
    model = Table
    template_name = "tables/tables_list.html"
    context_object_name = "tables"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        #Add active reservations for each table, updates automatically
        for table in context['tables']:
            table.active_reservations = table.reservations.filter(
                date__gte = today,
            ).order_by("date", "start_hour")
        
        return context

class ReservationCreateView(FormView):
    form_class = CreateReservationForm
    template_name = 'tables/make_reservation.html'
    success_url = reverse_lazy('tables:tables-list')

    def form_valid(self, form):
        date = form.cleaned_data["date"]
        selected_hours = sorted([int(h) for h in form.cleaned_data['time']])
        guests = form.cleaned_data["guests"]
        notes = form.cleaned_data["notes"]
        start_hour = selected_hours[0]
        end_hour = selected_hours[-1] + 1  # last hour + 1
        start_time_obj = time(hour = selected_hours[0])
        end_time_obj = time(hour = selected_hours[-1] + 1)

        # Automatically assign a table
        tables = Table.objects.filter(seats = guests)
        assigned_table = None
        for table in tables:
            conflict = Reservation.objects.filter(
                table=table,
                date=date,
                start_hour__lt = end_time_obj,
                end_hour__gt = start_time_obj
            ).exists()
            if not conflict:
                assigned_table = table
                break

        if not assigned_table:
            form.add_error('time', f"No table available from {start_hour}:00 to {end_hour}:00")
            return self.form_invalid(form)

        # Save reservation
        Reservation.objects.create(
            table = assigned_table,
            date = date,
            start_hour = start_time_obj,
            end_hour = end_time_obj,
            notes = notes,
            guests = guests
        )

        return super().form_valid(form)

def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, slug = pk)
    reservation.delete()
    return redirect("tables:tables-list")

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
            occupied_hours = set()

            for r in reserved:
                start = r.start_hour.hour
                end = r.end_hour.hour
                occupied_hours.update(range(start, end)) # Occupied hours for reservation
                available_hours = [(h, label) for h, label in table.HOURS_CHOICES if h not in occupied_hours]

            if requested_hours:
                available_hours = [(h, label) for h, label in available_hours if h in requested_hours_int]
     
            tables_with_availability[table.number] = available_hours

        context['availability'] = tables_with_availability
        return context
    
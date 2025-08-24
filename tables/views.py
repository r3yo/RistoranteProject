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
    form_class = ReservationForm
    template_name = 'tables/make_reservation.html'
    success_url = reverse_lazy('tables:tables-list')

    def form_valid(self, form):
        date = form.cleaned_data["date"]
        selected_hours = sorted([int(h) for h in form.cleaned_data['time']])
        num_people = form.cleaned_data["guests"]
        notes = form.cleaned_data["notes"]
        start_hour = selected_hours[0]
        end_hour = selected_hours[-1] + 1  # last hour + 1
        start_time_obj = time(hour = start_hour)
        end_time_obj = time(hour = end_hour)

        # Automatically assign a table
        tables = Table.objects.filter(seats = num_people)
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
            guests = num_people
        )

        return super().form_valid(form)

def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, slug = pk)
    reservation.status = "not_taken"
    reservation.save()
    return redirect("tables:tables-list")
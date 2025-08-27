from django.shortcuts import *
from django.views.generic import *
from django.shortcuts import *
from django.urls import *
from datetime import *
from django.contrib.auth.mixins import *
from django.contrib.auth.decorators import *
from braces.views import GroupRequiredMixin
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
        today = date.today()

        #Add active reservations for each table, updates automatically
        for table in context['tables']:
            table.active_reservations = table.reservations.filter(
                date__gte = today,
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

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = CreateReservationForm
    template_name = 'tables/make_reservation.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user      # pass user into the form constructor
        return kwargs

    def form_valid(self, form):
        return super().form_valid(form)

@login_required
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
    
from django.contrib import messages
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

class GroupRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "You need to log in to access this page.")
            return redirect("login")

        if not request.user.groups.filter(name__in=self.group_required).exists():
            messages.warning(request, "You don’t have permission to access this page.")
            return redirect("home")

        return super().dispatch(request, *args, **kwargs)

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
    ordering = ['number']

class TableDetailView(GroupRequiredMixin, DetailView):
    group_required = ["Managers"]
    model = Table
    context_object_name = "table"
    success_url = reverse_lazy('tables:tables-list')
    template_name = "tables/table_detail.html"

    def get_object(self, queryset = None):
        return get_object_or_404(Table, pk = self.kwargs.get("pk"))
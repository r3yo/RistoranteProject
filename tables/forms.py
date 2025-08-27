from .models import *
from django import forms
from django.utils import timezone
from django.db.models import Max

class TableForm(forms.ModelForm):

    seats = forms.IntegerField(min_value = 1)
   
    class Meta:
        model = Table
        fields = ['number', 'seats']
    
    def clean_seats(self):
        seats = self.cleaned_data['seats']
        table = self.instance  # the Table being updated
        # flat = True returns a flat list of values instead of tuples
        max_reserved = table.reservations.filter(date__gte=now().date()).order_by('-guests').values_list('guests', flat=True).first() or 0 # max_reserved is an integer, not a tuple
        if seats < max_reserved:
            raise forms.ValidationError(
                f"Cannot reduce seats below {max_reserved} because of existing reservations."
            )
        return seats

class ReservationForm(forms.ModelForm):

    guests = forms.IntegerField(label = "Number of Guests", min_value = 1)

    # Hours as multiple choices
    time = forms.MultipleChoiceField(
        choices = Table.HOURS_CHOICES,
        widget = forms.SelectMultiple(attrs={"size": "8"}),  # multi-select dropdown
        label = "Select Hour(s)",
        required = True
    )
    class Meta:
        model = Reservation
        fields = ['date', 'guests', 'notes', 'time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        self.fields['date'].widget = forms.DateInput(
            attrs = {
                'type': 'date',
                'min': today.strftime('%Y-%m-%d')
            }
        )

class CreateReservationForm(ReservationForm):
    
    notes = forms.CharField(required = False)

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        selected_hours = sorted([int(h) for h in cleaned_data.get('time', [])])

        cleaned_data['start_hour'] = time(hour  =selected_hours[0])
        cleaned_data['end_hour'] = time(hour = selected_hours[-1] + 1)

        # Automatic table assignment
        tables = Table.objects.filter(seats = cleaned_data['guests'])
        assigned_table = None

        for table in tables:
            if not Reservation.objects.filter(
                table=table,
                date=cleaned_data['date'],
                start_hour__lt = cleaned_data['end_hour'],
                end_hour__gt = cleaned_data['start_hour']
            ).exists():
                assigned_table = table
                break

        if assigned_table is None:
            raise forms.ValidationError("No table available for selected hours")

        cleaned_data['table'] = assigned_table
        return cleaned_data

    def save(self, commit=True):

        instance = super().save(commit = False)
        instance.start_hour = self.cleaned_data['start_hour']
        instance.end_hour = self.cleaned_data['end_hour']
        instance.table = self.cleaned_data['table']
        instance.user = self._user

        if commit:
            instance.save()
        return instance

class AvailabilityCheckForm(ReservationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['time'].required = False
    pass
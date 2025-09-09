from datetime import time
from reservations.utils import get_conflicting_reservations
from .models import *
from django import forms
from django.utils import timezone

class ReservationForm(forms.ModelForm):

    guests = forms.IntegerField(label = "Number of Guests", min_value = 1)

    # Hours as multiple choices
    time = forms.MultipleChoiceField(
        choices = Table.HOURS_CHOICES,
        widget = forms.SelectMultiple(attrs = {'size' : '8', 'id' : 'reservation-time'}),  # multi-select dropdown
        label = "Select Hour(s)",
        required = True
    )

    notes = forms.CharField(required = False)

    join_waitlist = forms.BooleanField(
        required = False,
        label = "Add me to the waitlist if no table is available"
    )

    class Meta:
        model = Reservation
        fields = ['date', 'guests', 'time', 'notes', 'join_waitlist']

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.waitlist_message = None

        today = timezone.localdate()
        self.fields['date'].widget = forms.DateInput(
            attrs = {
                'type': 'date',
                'min': today.strftime('%Y-%m-%d'),
                'id' : 'reservation-date'
            }
        )

    # Helpers
    def _get_time_range(self, cleaned_data):
        selected_hours = sorted(int(h) for h in cleaned_data.get("time", []))

        return time(hour = selected_hours[0]), time(hour = selected_hours[-1] + 1)

    def _get_valid_table(self, user, guests, date, start, end):
        """
        Find the first available table that fits the number of guests
        and is free during the requested time.
        Raises ValidationError if no table is available.
        """
        
        # If a client reserves, user will be None and its value will be the kwargs["user"] value, otherwise it will be the user value selected by the manager. This check is needed for consistency between errors

        if user == None:
            user = self._user

        my_table = None

        for table in Table.objects.filter(seats = guests).order_by('seats', 'number'):
            conflicts = get_conflicting_reservations(table, date, start, end)

            if self.instance.pk:
                conflicts = conflicts.exclude(pk = self.instance.pk)
            
            if conflicts.filter(user = user).exists():
                raise forms.ValidationError("You already have a reservation during this time.")

            if not conflicts.exists():
                my_table = table
                break

        return my_table

    # Main validation
    def clean(self):
        cleaned_data = super().clean()
        start, end = self._get_time_range(cleaned_data)
        cleaned_data["start_hour"] = start
        cleaned_data["end_hour"] = end

        table = self._get_valid_table(cleaned_data.get("user"), cleaned_data["guests"], cleaned_data["date"], start, end)   # cleaned_data.get("attr") returns the attr value if present, None otherwise
        cleaned_data["table"] = table  # could be None if no table available

        return cleaned_data

    # Save
    def save(self, commit = True):
        instance = super().save(commit = False)
        instance.start_hour = self.cleaned_data["start_hour"]
        instance.end_hour = self.cleaned_data["end_hour"]
        instance.table = self.cleaned_data["table"]

        if self._user and not instance.pk:
            instance.user = self._user

        if commit:
            instance.save()

        return instance

class ManagerReservationForm(ReservationForm):

    user = forms.ModelChoiceField(
        queryset = User.objects.exclude(is_superuser = True),
        required = True,
        label = "Select User"
    )

    class Meta(ReservationForm.Meta):
        fields = ['user'] + ReservationForm.Meta.fields
    
    def save(self, commit = True):
        instance = super().save(commit = False)
        # Use the user selected by the manager

        instance.user = self.cleaned_data["user"]

        if commit:
            instance.save()

        return instance

class AvailabilityCheckForm(ReservationForm):

    class Meta(ReservationForm.Meta):
        fields = ['date', 'guests', 'time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ['notes', 'join_waitlist']:
            if field in self.fields:
                del self.fields[field]
    
        self.fields['time'].required = False
        self.fields['guests'].required = False
    
    def clean(self):
        # Just return cleaned_data as-is, no table assignment or conflict checks
        return super(forms.ModelForm, self).clean()
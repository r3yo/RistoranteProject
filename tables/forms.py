from .models import *
from django import forms
from django.utils import timezone

class ReservationForm(forms.Form):
    date = forms.DateField()
    guests = forms.IntegerField(label = "Number of Guests")

    # Hours as multiple choices
    time = forms.MultipleChoiceField(
        choices = Table.HOURS_CHOICES,
        widget = forms.SelectMultiple(attrs={"size": "8"}),  # multi-select dropdown
        label = "Select Hour(s)",
        required = False
    )

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

class AvailabilityCheckForm(ReservationForm):
    pass
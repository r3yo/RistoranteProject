from .models import *
from django import forms
from django.utils import timezone
from datetime import datetime

class ReservationForm(forms.Form):
    date = forms.DateField(widget = forms.SelectDateWidget)
    guests = forms.IntegerField(label = "Number of Guests")

    # Hours as multiple choices
    HOURS_CHOICES = [(h, f"{h}:00 - {h+1}:00") for h in list(range(10, 15)) + list(range(19, 24))]
    time = forms.MultipleChoiceField(
        choices = HOURS_CHOICES,
        widget = forms.SelectMultiple(attrs={"size": "8"}),  # multi-select dropdown
        label = "Select Hour(s)"
    )
    notes = forms.CharField(required = False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate()
        now_hour = timezone.localtime().hour

        self.fields['date'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'min': today.strftime('%Y-%m-%d')  # only allow today or later
            }
        )
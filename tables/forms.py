from .models import *
from django import forms
from django.utils import timezone

class TableForm(forms.ModelForm):

    seats = forms.IntegerField(min_value = 1)

    number = forms.IntegerField(min_value = 1)
   
    class Meta:
        model = Table
        fields = ['number', 'seats']
    
    def clean_seats(self):
        seats = self.cleaned_data['seats']
        table = self.instance  # the Table being updated
        # flat = True returns a flat list of values instead of tuples
        max_reserved = table.reservations.filter(date__gte = timezone.localdate()).order_by('-guests').values_list('guests', flat=True).first() or 0 # max_reserved is an integer, not a tuple
        if seats < max_reserved:
            raise forms.ValidationError(
                f"Cannot reduce seats below {max_reserved} because of existing reservations."
            )
        return seats
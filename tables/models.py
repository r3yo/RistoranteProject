from django.db import models
from datetime import *
from django.utils.timezone import *
from django.db.models import Q
import random
import string

# Create your models here.

class Table(models.Model):

    HOURS_CHOICES = [(h, f"{h}:00 - {h+1}:00") for h in list(range(10, 15)) + list(range(19, 23))]
    
    number = models.IntegerField(unique = True)
    seats = models.IntegerField()
    slug = models.SlugField(primary_key = True, unique = True, blank = True)

    class Meta:
        verbose_name_plural = "Tables"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"table-{self.number}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Table {self.number} - Seats {self.seats}"

class Reservation(models.Model):

    table = models.ForeignKey(Table, on_delete = models.CASCADE, related_name = "reservations")
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    notes = models.TextField(blank = True)
    guests = models.IntegerField()
    slug = models.SlugField(primary_key = True, unique = True, blank = True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check = Q(guests__gt = 0),
                name = 'guests_positive'
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def generate_unique_slug(self):
        while True:
            slug = f"R-{random.choice(string.ascii_uppercase)}{random.randint(1000,9999)}"
            if not Reservation.objects.filter(slug=slug).exists():
                return slug

    def __str__(self):
        return f"Reservation for {self.guests} at {self.start_hour} on {self.date}"
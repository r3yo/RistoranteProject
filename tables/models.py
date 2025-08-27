import uuid
from django.db import models
from datetime import *
from django.utils.timezone import *
from django.db.models import Q
from django.contrib.auth.models import User
import random
import string

# Create your models here.
def generate_unique_slug(model, prefix):
    while True:
        slug = f"{prefix}-{random.choice(string.ascii_uppercase)}{random.randint(1000,9999)}"
        if not model.objects.filter(slug = slug).exists():
            return slug

class Table(models.Model):

    HOURS_CHOICES = [(h, f"{h}:00 - {h+1}:00") for h in list(range(10, 15)) + list(range(19, 23))]
    
    number = models.IntegerField(unique = True)
    seats = models.IntegerField()
    slug = models.SlugField(primary_key = True, unique = True, blank = True)

    class Meta:
        verbose_name_plural = "Tables"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Table, "TBL")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Table {self.number} - Seats {self.seats}"

class Reservation(models.Model):

    user = models.ForeignKey(User, on_delete = models.PROTECT, blank = True, related_name = "reservations")
    table = models.ForeignKey(Table, on_delete = models.CASCADE, related_name = "reservations")
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    notes = models.CharField(blank = True)
    guests = models.IntegerField()
    slug = models.SlugField(primary_key = True, unique = True, blank = True)

    def save(self, *args, **kwargs):  
        if not self.slug:
            self.slug = generate_unique_slug(Reservation, "R")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation for {self.guests} at {self.start_hour} on {self.date}"
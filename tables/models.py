from django.db import models
from datetime import *
from django.utils import timezone
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
    
    def active_reservations(self):
        return self.reservations.filter(date__gte = timezone.localdate()).order_by("date", "start_hour")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Table, "TBL")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Table {self.number} - Seats {self.seats}"
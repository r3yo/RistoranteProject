from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from tables.models import Table, generate_unique_slug

# Create your models here.
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

class WaitlistEntry(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "waitlist_entry")
    date = models.DateField()
    start_hour = models.TimeField()
    end_hour = models.TimeField()
    guests = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        verbose_name_plural = "Waitlist Entries"
        ordering = ['created_at']
        unique_together = ("user", "date", "start_hour", "end_hour")
    
    def __str__(self):
        return f"{self.user} in waiting list for {self.start_hour}-{self.end_hour} on {self.date} for {self.guests} guests."
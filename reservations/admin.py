from django.contrib import admin
from reservations.models import *

# Register your models here.
admin.site.register(Reservation)
admin.site.register(WaitlistEntry)
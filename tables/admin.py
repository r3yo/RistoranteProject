from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Table)
admin.site.register(Reservation)
admin.site.register(WaitlistEntry)
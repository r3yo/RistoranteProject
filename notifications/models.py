from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIF_TYPES = [
        ('CONFIRM', 'Confirmation'),
        ('REMINDER', 'Reminder'),
        ('UPDATE', 'Update'),
    ]
    
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length = 10, choices = NOTIF_TYPES)
    created_at = models.DateTimeField(auto_now_add = True)
    read = models.BooleanField(default = False)
    
    def __str__(self):
        return f"{self.type} for {self.user.username} at {self.created_at}"
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class CreateClientForm(CreateUserForm):
    def save(self, commit = True):
        user = super().save(commit)
        g = Group.objects.get(name = "Clients")
        g.user_set.add(user)
        return user
    
class CreateManagerForm(CreateUserForm):
    def save(self, commit = True):
        user = super().save(commit)
        g = Group.objects.get(name = "Managers")
        g.user_set.add(user)
        return user
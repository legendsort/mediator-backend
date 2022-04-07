from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from Account.models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'real_name', 'role')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'real_name', 'role')

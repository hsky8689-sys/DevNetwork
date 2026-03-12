from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User, UserProfileSection


class UserRegisterForm(UserCreationForm):
    email = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    birthday = forms.DateField()
    class Meta:
        model = User
        fields = ["username","email","password","birthday"]
class UserProfileSectionForm():
    name = forms.CharField(max_length=100,blank=False)
    content = forms.CharField(max_length=500,blank=False)
    hidden = forms.BooleanField()
    class Meta:
        model = UserProfileSection

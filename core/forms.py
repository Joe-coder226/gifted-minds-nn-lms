from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class AdminSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

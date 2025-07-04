#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'excel_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()



forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label="Name")
    email = forms.EmailField(label="Email")
    mobile = forms.CharField(max_length=15, label="Mobile Number")
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'email', 'mobile', 'password', 'confirm_password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match")

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Mobile Number")
    password = forms.CharField(widget=forms.PasswordInput)

views.pt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import RegistrationForm, CustomLoginForm

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['mobile']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=mobile, email=email, password=password, first_name=name)
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            mobile = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=mobile, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Change 'home' to your app's home page
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

login.html


<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; }
        .login-container { max-width: 400px; margin: 50px auto; padding: 40px; background: #fff; border-radius: 8px; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { width: 100%; padding: 10px; background: #1976d2; color: #fff; border: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login</h2>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="{% url 'register' %}">Register</a></p>
    </div>
</body>
</html>


registration.html
<!DOCTYPE html>
<html>
<head>
    <title>Register</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; }
        .register-container { max-width: 400px; margin: 50px auto; padding: 40px; background: #fff; border-radius: 8px; }
        input { width: 100%; padding: 10px; margin: 10px 0; }
        button { width: 100%; padding: 10px; background: #388e3c; color: #fff; border: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="register-container">
        <h2>Register</h2>
        <form method="post">
            {% csrf_token %}
            {{ form.as_p }}
            <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="{% url 'login' %}">Login</a></p>
    </div>
</body>
</html>
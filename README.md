


# django



models.py
from django.db import models

class UserDetail(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords

    def __str__(self):
        return self.mobile



views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserDetail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
import re

def is_valid_mobile(mobile):
    return re.match(r'^[6-9]\d{9}$', mobile)

def is_strong_password(password):
    return len(password) >= 6 and re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password)

def register(request):
    if request.method == 'POST':
        name = request.POST['name'].strip()
        email = request.POST['email'].strip()
        mobile = request.POST['mobile'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email format.")
            return redirect('register')

        # Mobile validation
        if not is_valid_mobile(mobile):
            messages.error(request, "Enter valid 10-digit mobile number starting with 6-9.")
            return redirect('register')

        # Password validation
        if not is_strong_password(password):
            messages.error(request, "Password must be at least 6 characters and include uppercase, lowercase, and number.")
            return redirect('register')

        # Confirm password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check for existing user
        if UserDetail.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered.")
            return redirect('register')
        if UserDetail.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('register')

        # Save user
        hashed_password = make_password(password)
        user = UserDetail(name=name, email=email, mobile=mobile, password=hashed_password)
        user.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        mobile = request.POST['mobile']
        password = request.POST['password']

        try:
            user = UserDetail.objects.get(mobile=mobile)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                messages.success(request, f"Welcome {user.name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Incorrect password.")
                return redirect('login')
        except UserDetail.DoesNotExist:
            messages.error(request, "Mobile number not found.")
            return redirect('login')

    return render(request, 'login.html')


def dashboard(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'dashboard.html', {'name': request.session['user_name']})


register.html

<!DOCTYPE html>
<html>
<head>
    <title>Register</title>
</head>
<body>
<h2>Register</h2>
<form method="POST">
    {% csrf_token %}
    <input type="text" name="name" placeholder="Name" required><br>
    <input type="email" name="email" placeholder="Email" required><br>
    <input type="text" name="mobile" placeholder="Mobile Number" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <input type="password" name="confirm_password" placeholder="Confirm Password" required><br>
    <button type="submit">Register</button>
</form>

{% for msg in messages %}
    <p style="color:red">{{ msg }}</p>
{% endfor %}
</body>
</html>


login.html
<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
<h2>Login</h2>
<form method="POST">
    {% csrf_token %}
    <input type="text" name="mobile" placeholder="Mobile Number" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Login</button>
</form>

{% for msg in messages %}
    <p style="color:red">{{ msg }}</p>
{% endfor %}
</body>
</html>
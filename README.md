


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



new  
def sync_data(df, unique_fields, s1, s2, s3, s4):
    # ------------------------- 1.  Normalise the payload ---------------------
    mapping   = {"name": s1, "mn": s2, "language": s3, "gender": s4}
    reverse   = {"item2": "name", "item3": "mn", "item4": "language", "item5": "gender"}

    df = df[[v for v in mapping.values()]].copy()          # keep only mapped columns
    df.columns = list(mapping.keys())                      # rename to model-field names

    if not unique_fields:
        raise ValueError("At least one unique field is required")

    mm = reverse[unique_fields[0]]                         # the column you marked UNIQUE
    df[mm] = df[mm].astype(str).str.strip()
    df = df.dropna(subset=[mm])

    # ------------------------- 2.  Lookup existing objects -------------------
    existing = {getattr(e, mm): e for e in Employe.objects.all()}

    new_keys     = set(df[mm]) - existing.keys()
    update_keys  = set(df[mm]) & existing.keys()
    delete_keys  = existing.keys()  - set(df[mm])

    # ------------------------- 3.  INSERT new rows ---------------------------
    Employe.objects.bulk_create(
        Employe(**row._asdict())
        for row in df[df[mm].isin(new_keys)].itertuples(index=False)
    )

    # ------------------------- 4.  UPDATE existing rows ----------------------
    for row in df[df[mm].isin(update_keys)].itertuples(index=False):
        obj = existing[getattr(row, mm)]
        for field in ["name", "mn", "language", "gender"]:
            setattr(obj, field, getattr(row, field))
        obj.save()

    # ------------------------- 5.  DELETE missing rows -----------------------
    Employe.objects.filter(**{f"{mm}__in": list(delete_keys)}).delete()





newewww



# views.py  — drop this straight into your Django app
# -----------------------------------------------
from functools import wraps

import pandas as pd
import re

from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.db import connection
from django.shortcuts import render, redirect

from .models import Employe, UserDetail


# ---------------------------------------------------------------------------
# Globals reused across the 2-step upload workflow
# ---------------------------------------------------------------------------
uploaded_data = pd.DataFrame()
items = []


# ---------------------------------------------------------------------------
# Session-based auth helpers
# ---------------------------------------------------------------------------
def login_required_custom(view_func):
    """
    Mini-version of Django’s @login_required.
    Redirects to 'login' unless request.session['user_id'] is present.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return _wrapped


# ---------------------------------------------------------------------------
# Registration / Login / Logout
# ---------------------------------------------------------------------------
def register(request):
    if request.method == "POST":
        name     = request.POST["name"].strip()
        email    = request.POST["email"].strip()
        mobile   = request.POST["mobile"].strip()
        password = request.POST["password"]
        cpwd     = request.POST["confirm_password"]

        errors = []

        # --- validations ----------------------------------------------------
        if not re.match(r"^\d{10}$", mobile):
            errors.append("Mobile number is invalid.")

        if password != cpwd:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character.")

        if not all([name, email, mobile, password, cpwd]):
            errors.append("All fields are required.")

        if UserDetail.objects.filter(mobile=mobile).exists():
            errors.append("Mobile number already registered.")
        if UserDetail.objects.filter(email=email).exists():
            errors.append("Email already registered.")

        if errors:
            return render(request, "register.html", {"errors": errors})

        # --- create user ----------------------------------------------------
        try:
            UserDetail.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                password=make_password(password),
            )
            messages.success(request, "Registration successful. Please log in.")
            return redirect("login")
        except Exception as exc:
            return render(request, "register.html", {"error": str(exc)})

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        mobile   = request.POST["mobile"]
        password = request.POST["password"]

        try:
            user = UserDetail.objects.get(mobile=mobile)
        except UserDetail.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect("login")

        if not check_password(password, user.password):
            messages.error(request, "Incorrect password.")
            return redirect("login")

        # -------- successful login -----------------------------------------
        request.session["user_id"]          = user.id
        request.session["user_name"]        = user.name
        request.session["is_authenticated"] = True  # handy in templates
        return redirect("upload")

    return render(request, "login.html")


def logout_view(request):
    request.session.flush()
    return redirect("login")


# ---------------------------------------------------------------------------
# Step-1  File upload
# ---------------------------------------------------------------------------
@login_required_custom
def upload_file(request):
    global uploaded_data, items

    if request.method == "POST":
        excel_file = request.FILES.get("file")
        if not excel_file:
            return render(request, "select1.html", {"error": "No file selected."})

        try:
            uploaded_data = pd.read_excel(excel_file)
            uploaded_data.columns = uploaded_data.columns.str.strip()
            items = uploaded_data.columns.to_list()

            # keep everything across the redirect
            request.session["items"] = items
            request.session["data"]  = uploaded_data.to_json()
            return redirect("map_columns")
        except Exception as exc:
            return render(request, "select1.html", {"error": str(exc)})

    return render(request, "select1.html")


# ---------------------------------------------------------------------------
# Step-2  Column mapping & DB sync
# ---------------------------------------------------------------------------
@login_required_custom
def map_columns(request):
    global uploaded_data, items
    items         = request.session.get("items", [])
    uploaded_data = pd.read_json(request.session.get("data", "{}"))

    if request.method == "POST":
        selection = [
            request.POST.get("selected_item1"),
            request.POST.get("selected_item2"),
            request.POST.get("selected_item3"),
            request.POST.get("selected_item4"),
        ]
        unique_fields = [
            key for key in ["item2", "item3", "item4", "item5"]
            if request.POST.get(key)
        ]

        if "" in selection or None in selection:
            return render(request, "select2.html",
                          {"items": items, "error": "Please select columns."})
        if len(selection) != len(set(selection)):
            return render(request, "select2.html",
                          {"items": items, "error": "Please select different columns."})

        try:
            set_unique_constraints(unique_fields)
            sync_data(uploaded_data, unique_fields, *selection)
            return render(request, "select2.html",
                          {"items": items, "success": "Data inserted successfully."})
        except Exception as exc:
            return render(request, "select2.html",
                          {"items": items, "error": str(exc)})

    return render(request, "select2.html", {"items": items})


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------
def set_unique_constraints(fields):
    mapping = {
        "item2": "name",
        "item3": "mn",
        "item4": "language",
        "item5": "gender",
    }
    with connection.cursor() as cursor:
        for field_key in fields:
            column = mapping[field_key]
            try:
                cursor.execute(f"ALTER TABLE excelapp_employe ADD UNIQUE ({column});")
            except Exception:
                # Ignore “duplicate key” errors if constraint already exists
                pass


def sync_data(df, fields, s1, s2, s3, s4):
    mapping_in = {"name": s1, "mn": s2, "language": s3, "gender": s4}
    mapping_ref = {
        "item2": "name",
        "item3": "mn",
        "item4": "language",
        "item5": "gender",
    }

    # reshape dataframe
    df = df[[v for v in mapping_in.values()]].copy()
    df.columns = list(mapping_in.keys())

    # choose the “natural key” column (first field checked by the user)
    mm = mapping_ref[fields[0]] if fields else "mn"  # sensible default
    df[mm] = df[mm].astype(str).str.strip()
    df.dropna(subset=[mm], inplace=True)

    # current DB snapshot
    existing = {getattr(e, mm): e for e in Employe.objects.all()}

    new_ids    = set(df[mm]) - existing.keys()
    update_ids = set(df[mm]) & existing.keys()
    delete_ids = existing.keys() - set(df[mm])

    # -------- inserts ------------------------------------------------------
    Employe.objects.bulk_create(
        [Employe(**row._asdict())
         for row in df[df[mm].isin(new_ids)].itertuples(index=False)]
    )

    # -------- updates ------------------------------------------------------
    for row in df[df[mm].isin(update_ids)].itertuples(index=False):
        obj = existing[getattr(row, mm)]
        for field in ["name", "mn", "language", "gender"]:
            setattr(obj, field, getattr(row, field))
        obj.save()

    # -------- deletes ------------------------------------------------------
    Employe.objects.filter(**{f"{mm}__in": list(delete_ids)}).delete()
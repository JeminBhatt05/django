from django.contrib import messages
import pandas as pd
from django.shortcuts import render, redirect
import re
from .models import Employe
from django.db import connection
from .models import UserDetail
from django.contrib.auth.hashers import make_password, check_password





uploaded_data = pd.DataFrame()
items = []

def register(request):
    if request.method == "POST":
        
        name = request.POST['name'].strip()
        email = request.POST['email'].strip()
        mobile = request.POST['mobile'].strip()
        password = request.POST['password']
        cpwd = request.POST['confirm_password']
        errors = []

        
        pattern = r'^\d{10}$' 
        if not re.match(pattern, mobile):    
            errors.append("Mobile number is invalid")
    
    
        
        if password != cpwd:
            errors.append("Passwords do not match.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")

        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter.")

        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter.")

        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character.")


        if not name or not password or not mobile or not password or not cpwd :
            return render(request, 'register.html', {'error': 'All fields are required.'})
        
        if UserDetail.objects.filter(mobile=mobile).exists():
            errors.append("Mobile number already registered.")
            
        if UserDetail.objects.filter(email=email).exists():
            errors.append( "Email already registered.")
            
        if errors: 
            
            return render(request, 'register.html', {'errors': errors})
        
        try:
            hashed_password = make_password(password)
            user = UserDetail(name=name, email=email, mobile=mobile, password=hashed_password)
            user.save()
            return render(request, 'login.html')
        except Exception as e:
            return render(request, 'register.html',{'error': str(e)})

        
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

                return redirect('upload')
            else:
                messages.error(request, "Incorrect password.")
                return redirect('login')
        except UserDetail.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

    return render(request, 'login.html')

def upload_file(request):
    global uploaded_data, items

    if request.method == 'POST':
        # form = UploadFileForm(request.POST, request.FILES)
        # if form.is_valid():
            excel_file = request.FILES['file']
            try:
                uploaded_data = pd.read_excel(excel_file)
                uploaded_data.columns = uploaded_data.columns.str.strip()
                items = uploaded_data.columns.to_list()
                request.session['items'] = items
                request.session['data'] = uploaded_data.to_json()
                return redirect('map_columns')
            except Exception as e:
                return render(request, 'select1.html', )
            
    # else:
    #     form = UploadFileForm()

    return render(request, 'select1.html')


def map_columns(request):
    global uploaded_data, items

    items = request.session.get('items', [])
    uploaded_data = pd.read_json(request.session.get('data'))

    if request.method == 'POST':
        selection = [
            
            request.POST.get('selected_item1'),
            request.POST.get('selected_item2'),
            request.POST.get('selected_item3'),
            request.POST.get('selected_item4')
        ]
    
        unique_fields = [key for key in ['item2', 'item3', 'item4', 'item5'] if request.POST.get(key)]
        if selection=="":
            return render(request, 'select2.html', {'items': items, 'error': "Please select columns."})
        if len(selection) != len(set(selection)):
            return render(request, 'select2.html', {'items': items, 'error': "Please select different columns."})

        try:
            set_unique_constraints(unique_fields)
            sync_data(uploaded_data,unique_fields, *selection)
            return render(request, 'select2.html', {'items': items, 'success': "Data inserted successfully."})
        except Exception as e:
            return render(request, 'select2.html', {'items': items, 'error': str(e)})

    return render(request, 'select2.html', {'items': items})


def set_unique_constraints(fields):
    mapping = {
            
        'item2': 'name',
        'item3': 'mn',
        'item4': 'language',
        'item5': 'gender'
    }

    with connection.cursor() as cursor:
        for item in fields:
            try:
                sql = f"ALTER TABLE excelapp_employe ADD UNIQUE ({mapping[item]});"
                cursor.execute(sql)
            except:
                pass  # Avoid duplicate unique constraint error


def sync_data(df,fields, s1, s2, s3, s4):
    mapping = {'name': s1, 'mn': s2, 'language': s3, 'gender': s4}
    mapping1 = {
        
        'item2': 'name',
        'item3': 'mn',
        'item4': 'language',
        'item5': 'gender'
    }
    df = df[[v for v in mapping.values()]].copy()
    
    df.columns = list(mapping.keys())
    for item in fields:
        try:
            mm=mapping1[item]
        except:
            
            pass
            
    df[mm] = df[mm].astype(str).str.strip()
    df = df.dropna(subset=[mm])
    
    print(mm)
    existing = {e.mm:e for e in Employe.objects.all()}
    
    
    
    print("hello",existing)
    
    new_ids = set(df[mm]) - set(existing.keys())
    update_ids = set(df[mm]) & set(existing.keys())
    delete_ids = set(existing.keys()) - set(df[mm])

    # Insert new
    Employe.objects.bulk_create([
        Employe(**row._asdict()) for row in df[df[mm].isin(new_ids)].itertuples(index=False)
    ])

    # Update existing
    for row in df[df[mm].isin(update_ids)].itertuples(index=False):
        obj = existing[row.mm]
        for field in ['name', 'mn', 'language', 'gender']:
            setattr(obj, field, getattr(row, field))    
        obj.save() 

    # Delete missing
    Employe.objects.filter(id__in=delete_ids).delete()



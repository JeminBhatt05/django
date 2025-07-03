import os
import pandas as pd
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import Employe
from django.conf import settings
from django.db import connection, transaction

uploaded_data = pd.DataFrame()
items = []

def upload_file(request):
    global uploaded_data, items

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            try:
                uploaded_data = pd.read_excel(excel_file)
                uploaded_data.columns = uploaded_data.columns.str.strip()
                items = uploaded_data.columns.to_list()
                request.session['items'] = items
                request.session['data'] = uploaded_data.to_json()
                return redirect('map_columns')
            except Exception as e:
                return render(request, 'select1.html', {'form': form, 'error': str(e)})
    else:
        form = UploadFileForm()

    return render(request, 'select1.html', {'form': form})


def map_columns(request):
    global uploaded_data, items

    items = request.session.get('items', [])
    uploaded_data = pd.read_json(request.session.get('data'))

    if request.method == 'POST':
        selection = [
            request.POST.get('selected_item'),
            request.POST.get('selected_item1'),
            request.POST.get('selected_item2'),
            request.POST.get('selected_item3'),
            request.POST.get('selected_item4')
        ]
        unique_fields = [key for key in ['item1', 'item2', 'item3', 'item4', 'item5'] if request.POST.get(key)]

        if len(selection) != len(set(selection)):
            return render(request, 'select2.html', {'items': items, 'error': "Please select different columns."})

        try:
            set_unique_constraints(unique_fields)
            sync_data(uploaded_data, *selection)
            return render(request, 'select2.html', {'items': items, 'success': "Data inserted successfully."})
        except Exception as e:
            return render(request, 'select2.html', {'items': items, 'error': str(e)})

    return render(request, 'select2.html', {'items': items})


def set_unique_constraints(fields):
    mapping = {
        'item1': 'id',
        'item2': 'name',
        'item3': 'mn',
        'item4': 'language',
        'item5': 'gender'
    }

    with connection.cursor() as cursor:
        for item in fields:
            try:
                sql = f"ALTER TABLE your_app_employe ADD UNIQUE ({mapping[item]});"
                cursor.execute(sql)
            except:
                pass  # Avoid duplicate unique constraint error


def sync_data(df, s, s1, s2, s3, s4):
    mapping = {'id': s, 'name': s1, 'mn': s2, 'language': s3, 'gender': s4}
    df = df[[v for v in mapping.values()]].copy()
    df.columns = list(mapping.keys())
    df['id'] = df['id'].astype(str).str.strip()
    df = df.dropna(subset=['id'])

    existing = {e.id: e for e in Employe.objects.all()}

    new_ids = set(df['id']) - set(existing.keys())
    update_ids = set(df['id']) & set(existing.keys())
    delete_ids = set(existing.keys()) - set(df['id'])

    # Insert new
    Employe.objects.bulk_create([
        Employe(**row._asdict()) for row in df[df['id'].isin(new_ids)].itertuples(index=False)
    ])

    # Update existing
    for row in df[df['id'].isin(update_ids)].itertuples(index=False):
        obj = existing[row.id]
        for field in ['name', 'mn', 'language', 'gender']:
            setattr(obj, field, getattr(row, field))
        obj.save()

    # Delete missing
    Employe.objects.filter(id__in=delete_ids).delete()

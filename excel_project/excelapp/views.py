from django.shortcuts import render,redirect
import pandas as pd
from .forms import UploadExcelForm
from .models import Person

def upload_excel(request):
    context={}
    
    
    if request.method=='POST' and 'file' in request.FILES:
        form=UploadExcelForm(request.POST,request.FILES)
        if form.is_valid():
            excel_file=request.FILES['file']
            df=pd.read_excel(excel_file)
            request.session['exce_data']=df.to_dict()
            request.session['exce_columns']=list(df.columns)
            context['columns']=list(df.columns)
            context['db_fields']=[f.name for f in Person._meta.fields if f.name !='id']
            return render(request,'map_columns.html',context)
    else:
        form=UploadExcelForm()
        
    return render(request,'upload.html',{'form':form})
    
    
def process_mapping(request):
    if request.method=='POST':
        column_map={}
        for key, value in request.POST.items():
            if key.startswith('map_') and value:
                db_field=key.replace('map_','')
                column_map[db_field]=value
                
        df=pd.DataFrame(request.session.get('excel_data'))
        
        
        existing_fids=set(Person.objects.values_list('fid',flat=True))
        incoming_fids=set(df[column_map['fid']])
        Person.objects.filter(fid__in=(existing_fids - incoming_fids)).delete()
        
        for _, row in df.iterrows():
            data={db:row[excel] for db, excel in column_map.items()}
            Person.objects.update_or_create(fid=data['fid'])
            
        return redirect('upload_excel')
    return redirect('upload_excel')

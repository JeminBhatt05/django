from django.urls import path
from . import views

urlpatterns = [
    path('upload/',views.upload_excel,name='upload_excel'),
    path('process/',views.process_mapping,name='process_mapping')
]

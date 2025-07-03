from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_file, name='upload'),
    path('map/', views.map_columns, name='map_columns'),
]

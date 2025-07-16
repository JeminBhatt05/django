from django.urls import path
from . import views
# from .views import register, login_view
urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('upload/', views.upload_file, name='upload'),
    path('map/', views.map_columns, name='map_columns'),
]

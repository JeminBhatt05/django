from django.db import models
import re
from django.contrib.auth.hashers import make_password, check_password
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django import forms




# class UploadFileForm(forms.Form):
#     file = forms.FileField()

class Employe(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    mn = models.CharField(max_length=15)
    language = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class UserDetail(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords

    def __str__(self):
        return self.mobile

    


class CustomLoginForm(AuthenticationForm):
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=100)    
    
    

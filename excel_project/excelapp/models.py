from django.db import models

# Create your models here.
class Person(models.Model):
    fid=models.IntegerField(unique=True)
    name=models.CharField(max_length=100)
    num=models.CharField(max_length=100)
    language=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
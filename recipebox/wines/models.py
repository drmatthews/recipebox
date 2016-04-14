from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class WineNote(models.Model):
    user = models.OneToOneField(User, unique=True,null=True)
    title = models.CharField(max_length=200)
    producer = models.CharField(max_length=200)
    description = models.TextField(blank=True)  
    wine_picture_url = models.CharField(blank=True,max_length=500)    

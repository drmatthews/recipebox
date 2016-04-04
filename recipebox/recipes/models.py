from __future__ import absolute_import

from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class UserProfile(models.Model):
    user = models.OneToOneField(User,unique=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

class Recipe(models.Model):
    user = models.OneToOneField(User, unique=True,null=True)
    chef = models.CharField(blank=True,max_length=200)
    source = models.CharField(blank=True,max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    picture = models.ImageField(blank=True, null=True) #remember to bind to form

class RecipePicture(models.Model):
    recipe = models.OneToOneField(Recipe,unique=True)
    picture = models.ImageField(blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.recipe.title

class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient_name = models.CharField(max_length=500)

class MethodStep(models.Model):
    recipe = models.ForeignKey(Recipe)
    step = models.TextField(max_length=500)

class WineNote(models.Model):
    user = models.OneToOneField(User, unique=True,null=True)
    title = models.CharField(max_length=200)
    producer = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    picture = models.ImageField(blank=True, null=True) #remember to bind to form    
    

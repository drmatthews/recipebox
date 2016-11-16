from __future__ import absolute_import

from django.db import models
from django.conf import settings

from recipebox.wines.models import WineNote

User = settings.AUTH_USER_MODEL

class UserProfile(models.Model):
    user = models.OneToOneField(User,unique=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

class Recipe(models.Model):
    user = models.ForeignKey(User, null=True)
    chef = models.CharField(blank=True,max_length=200)
    source = models.CharField(blank=True,max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    recipe_picture = models.ImageField(upload_to='images',blank=True)
    recipe_thumbnail = models.ImageField(upload_to='thumbnails',blank=True) 
    matched_wine = models.ForeignKey(WineNote,blank=True,null=True,on_delete=models.SET_NULL,max_length=500)


    def create_thumbnail(self):
        # original code for this method came from
        # http://snipt.net/danfreak/generate-thumbnails-in-django-with-pil/

        # If there is no image associated with this.
        # do not create thumbnail
        print "self.image",self.recipe_picture
        if not self.recipe_picture:
            return

        from PIL import Image
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        DJANGO_TYPE = self.recipe_picture.file.content_type

        if DJANGO_TYPE == 'image/jpeg':
            PIL_TYPE = 'jpeg'
            FILE_EXTENSION = 'jpg'
        elif DJANGO_TYPE == 'image/png':
            PIL_TYPE = 'png'
            FILE_EXTENSION = 'png'

        # Open original photo which we want to thumbnail using PIL's Image
        img = Image.open(StringIO(self.recipe_picture.read()))

        size = (318,318)
        img_ratio = img.size[0] / float(img.size[1])
        ratio = size[0] / float(size[1])        

        if ratio > img_ratio:
            img = img.resize((size[0], size[0] * img.size[1] / img.size[0]),Image.ANTIALIAS)
            box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
            img = img.crop(box)
        elif ratio < img_ratio:
            img = img.resize((size[1] * img.size[0] / img.size[1], size[1]),Image.ANTIALIAS)
            box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
            img = img.crop(box)
        else :
            img = img.resize((size[0], size[1]),
                        Image.ANTIALIAS)

        # Save the thumbnail
        temp_handle = StringIO()
        img.save(temp_handle, PIL_TYPE)
        temp_handle.seek(0)

        # Save image to a SimpleUploadedFile which can be saved into
        # ImageField
        suf = SimpleUploadedFile(os.path.split(self.recipe_picture.name)[-1],
            temp_handle.read(), content_type=DJANGO_TYPE)
        # Save SimpleUploadedFile into image field
        self.recipe_thumbnail.save(
            '%s_thumbnail.%s' % (os.path.splitext(suf.name)[0], FILE_EXTENSION),
            suf,
            save=False
        )      

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

class ExternalRecipe(models.Model):
    source = models.CharField(blank=True,max_length=200)
    title_class = models.CharField(blank=True,max_length=200)
    chef_class = models.CharField(blank=True,max_length=200)    
    description_class = models.CharField(blank=True,max_length=200)
    ingredients_class = models.CharField(blank=True,max_length=200)    
    method_class = models.CharField(blank=True,max_length=200)    
    

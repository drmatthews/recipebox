# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-11 08:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='picture',
        ),
        migrations.AddField(
            model_name='recipe',
            name='recipe_picture',
            field=models.ImageField(blank=True, null=True, upload_to=b'recipe_pictures'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='recipe_picture_url',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
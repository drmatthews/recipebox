# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-20 07:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_recipe_search_index'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='search_index',
        ),
    ]
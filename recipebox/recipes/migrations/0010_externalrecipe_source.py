# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-08-21 10:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_externalrecipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalrecipe',
            name='source',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
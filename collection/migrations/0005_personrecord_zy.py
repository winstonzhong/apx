# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-12 10:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0004_personrecord_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='personrecord',
            name='zy',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='\u804c\u4e1a'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-08-04 04:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('names', '0002_auto_20170803_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='names',
            name='abandoned',
            field=models.BooleanField(default=False),
        ),
    ]

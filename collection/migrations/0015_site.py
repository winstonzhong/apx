# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-31 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0014_auto_20170731_1129'),
    ]

    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('domain', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('url', models.URLField()),
            ],
        ),
    ]

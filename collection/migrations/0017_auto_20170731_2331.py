# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-31 23:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0016_htmlcontent_corrupted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='htmlcontent',
            name='corrupted',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]

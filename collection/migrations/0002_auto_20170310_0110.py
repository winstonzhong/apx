# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-10 01:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personrecord',
            old_name='height',
            new_name='sg',
        ),
        migrations.RemoveField(
            model_name='personrecord',
            name='name',
        ),
        migrations.AddField(
            model_name='personrecord',
            name='csny',
            field=models.DateField(blank=True, null=True, verbose_name='\u51fa\u751f\u5e74\u6708'),
        ),
        migrations.AddField(
            model_name='personrecord',
            name='tz',
            field=models.FloatField(blank=True, null=True, verbose_name='\u4f53\u91cd'),
        ),
        migrations.AddField(
            model_name='personrecord',
            name='xb',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='\u6027\u522b'),
        ),
        migrations.AddField(
            model_name='personrecord',
            name='xx',
            field=models.CharField(blank=True, max_length=5, null=True, verbose_name='\u8840\u578b'),
        ),
        migrations.AddField(
            model_name='personrecord',
            name='xz',
            field=models.CharField(blank=True, max_length=8, null=True, verbose_name='\u661f\u5ea7'),
        ),
        migrations.AddField(
            model_name='personrecord',
            name='ywm',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='\u82f1\u6587\u540d\u79f0'),
        ),
        migrations.AddField(
            model_name='personrecord',
            name='zwm',
            field=models.CharField(default=django.utils.timezone.now, max_length=100, primary_key=True, serialize=False, verbose_name='\u4e2d\u6587\u540d'),
            preserve_default=False,
        ),
    ]
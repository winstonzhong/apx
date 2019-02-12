# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-23 10:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='\u4e2d\u6587\u540d')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, '\u4e3b\u8bed'), (2, '\u8c13\u8bed')], default=1, verbose_name='\u8bcd\u6027')),
            ],
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pred', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pred', to='mind.Element')),
                ('sub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sub', to='mind.Element')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='element',
            unique_together=set([('name', 'type')]),
        ),
        migrations.AlterIndexTogether(
            name='element',
            index_together=set([('name', 'type')]),
        ),
        migrations.AlterUniqueTogether(
            name='relation',
            unique_together=set([('sub', 'pred')]),
        ),
        migrations.AlterIndexTogether(
            name='relation',
            index_together=set([('sub', 'pred')]),
        ),
    ]
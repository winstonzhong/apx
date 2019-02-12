# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-27 13:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import training.adv_ligament


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0011_auto_20170313_1239'),
    ]

    operations = [
        migrations.CreateModel(
            name='HtmlContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('html', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='TitleEntity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eid', models.IntegerField()),
                ('trainee', models.BooleanField(default=False)),
                ('testee', models.BooleanField(default=False)),
                ('label', models.SmallIntegerField(default=0)),
                ('result', models.SmallIntegerField(blank=True, null=True)),
                ('pval', models.FloatField(blank=True, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=1)),
                ('memo', models.TextField(blank=True, null=True)),
                ('html', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.HtmlContent')),
            ],
            bases=(training.adv_ligament.AdvancedLigament, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='htmlcontent',
            unique_together=set([('url',)]),
        ),
        migrations.AlterIndexTogether(
            name='htmlcontent',
            index_together=set([('url',)]),
        ),
        migrations.AlterUniqueTogether(
            name='titleentity',
            unique_together=set([('html', 'eid')]),
        ),
        migrations.AlterIndexTogether(
            name='titleentity',
            index_together=set([('html', 'eid')]),
        ),
    ]
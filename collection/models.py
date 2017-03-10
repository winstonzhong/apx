# encoding: utf-8
from __future__ import unicode_literals

from django.db import models
from collection.tool_net import get_name_properties, get_index

# Create your models here.
class PersonRecord(models.Model):
    zwm = models.CharField(max_length=100, primary_key=True, verbose_name=u'中文名')
    ywm = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'英文名称')
    xb = models.CharField(max_length=5, blank=True, null=True, verbose_name=u'性别')
    sg = models.FloatField(blank=True, null=True, verbose_name=u'身高')
    tz = models.FloatField(blank=True, null=True, verbose_name=u'体重')
    xx = models.CharField(max_length=5, blank=True, null=True, verbose_name=u'血型')
    csny = models.DateField(blank=True, null=True, verbose_name=u'出生年月')
    xz = models.CharField(max_length=8, blank=True, null=True, verbose_name=u'星座')
    
    bd_index = models.IntegerField(blank=True, null=True, verbose_name=u'百度指数')
    
    
    @classmethod
    def get_field_names(cls):
        return map(lambda x:x.name, PersonRecord._meta.fields)
    
    @classmethod
    def add(cls, name):
        name = name.encode('utf8')
        d = get_name_properties(name)
        d['bd_index'] = get_index(name)
        d = {k:v for k,v in d.items() if k in cls.get_field_names()}
        cls.objects.get_or_create(zwm=d.get('zwm'), defaults=d)
        
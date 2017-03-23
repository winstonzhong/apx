# encoding: utf-8
from __future__ import unicode_literals

import base64
import json
import re
import zlib

from django.db import models
from django.db.models.aggregates import Sum, Avg, Min, Max, Count
from django.db.models.expressions import F
from django.db.models.query_utils import Q

from collection.tool_net import get_name_properties, get_index, \
    NoTableFoundError, NoPropertiesError, DumpPropertyError, JBQMNameParseError, \
    get_name_info, CODE_OTHER_EXCEPTIONS, get_english_info
from utils.tool_env import force_utf8, force_unicode, split_english_words


class CommonEnglishNames(models.Model):
    name = models.CharField(max_length=100, primary_key=True, verbose_name=u'英文名')
    sex = models.NullBooleanField(null=True, blank=True)
    sex_count = models.SmallIntegerField(default=0)
    
    def save(self, force_insert=False, force_update=False, using=None, 
        update_fields=None):
        if self.sex == 1:
            self.sex_count +=1
        elif self.sex == 0:
            self.sex_count -=1
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
    
    @classmethod
    def get_unique_words(cls, name, notin=['lee', 'lin']):
        if name:
            words = map(lambda x:x.strip(), split_english_words(name))
            words = filter(lambda x:x not in notin, words)
            return map(lambda x:x.values()[0], cls.objects.filter(name__in=words).values('name'))
#             return cls.objects.filter(name__in=words).aggregate(Sum('sex_count')).values()[0]
        
    @classmethod
    def get_english_name_gender_count(cls, name):
        if name:
#             words = map(lambda x:x.strip(), re.split('\s+', name.lower()))
            words = map(lambda x:x.strip(), split_english_words(name))
            return cls.objects.filter(name__in=words).aggregate(Sum('sex_count')).values()[0]

class PersonRecord(models.Model):
    zwm = models.CharField(max_length=100, primary_key=True, verbose_name=u'中文名')
    ywm = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'英文名称')
    xb = models.CharField(max_length=5, blank=True, null=True, verbose_name=u'性别')
    sg = models.FloatField(blank=True, null=True, verbose_name=u'身高')
    tz = models.FloatField(blank=True, null=True, verbose_name=u'体重')
    xx = models.CharField(max_length=5, blank=True, null=True, verbose_name=u'血型')
    csny = models.DateField(blank=True, null=True, verbose_name=u'出生年月')
    qsny = models.DateField(blank=True, null=True, verbose_name=u'去世年月')
    xz = models.CharField(max_length=8, blank=True, null=True, verbose_name=u'星座')
    zy = models.CharField(max_length=8, blank=True, null=True, verbose_name=u'职业')
    
    
    bd_index = models.IntegerField(blank=True, null=True, verbose_name=u'百度指数')
    
    all_props = models.BinaryField(blank=True, null=True, verbose_name=u'所有属性')
    
    updated = models.PositiveSmallIntegerField(blank=True, null=True)
    
    name_shuli = models.CharField(max_length=100, blank=True, null=True, verbose_name=u'金榜数理')
    
    english_info = models.TextField(blank=True, null=True, verbose_name=u'英文名词典')


    def cddq(self):
        d = self.get_all_props()
        return d.get('cddq', '')
    cddq.short_description = u'出道地区'

    def gj(self):
        d = self.get_all_props()
        return d.get('gj', '')
    gj.short_description = u'贯籍'


    def tinfo(self):
        return u"<a href='http://www.baike.com/wiki/%s' target=blank>百科</a>" % (force_unicode(self.zwm))
    tinfo.allow_tags = True
    tinfo.short_description = u'信息源'
    
    
    def get_all_props(self):
        return json.loads(zlib.decompress(base64.b64decode(self.all_props))) if self.all_props is not None else {}
        
    @classmethod
    def get_field_names(cls):
        return map(lambda x:x.name, PersonRecord._meta.fields)
    
    @classmethod
    def add(cls, name):
        # 编码为utf8
        name = force_utf8(name)
#         print name
        # 创建或者取出一条符合要求的记录
        #  1. 如果没有记录, 则创建;
        #  2. 如果有记录, 则取出该条记录.
        pr, _ = cls.objects.get_or_create(zwm=name, defaults= {'bd_index':get_index(name)})
        return pr
        
    @classmethod
    def dump_props(cls, d):
        try:
            return base64.b64encode(zlib.compress(json.dumps(d)))
        except Exception:
            raise DumpPropertyError
    
    
    @classmethod
    def get_english_info(cls, name):
        if name:
            words = split_english_words(name)
            d = {x:get_english_info(x) for x in words}
            return json.dumps(d)
        
    
    @classmethod
    def update(cls, name):
        try:
            # 编码为utf8
            name = force_utf8(name)
            
            d, relations = get_name_properties(name)

            d['zwm'] = name
            
            d['all_props'] = cls.dump_props(d)
            
            d['name_shuli'] = get_name_info(name)
            
            d['english_info'] = cls.get_english_info(d.get('ywm'))
            
            d['updated'] = 1
            
            d = {k:v for k,v in d.items() if k in cls.get_field_names()}
            cls.objects.update_or_create(zwm=d.get('zwm'), defaults=d)
            for x in relations:
                cls.add(x)

        except (NoTableFoundError,NoPropertiesError, DumpPropertyError, JBQMNameParseError) as e:
            cls.objects.update_or_create(zwm=name, defaults={'updated':e.code})
        except Exception as e:
            print e
            cls.objects.update_or_create(zwm=name, defaults={'updated':CODE_OTHER_EXCEPTIONS})
            
    @classmethod
    def get_person_not_updated(cls):
        pr = PersonRecord.objects.filter(updated=None).order_by('-bd_index').first() or cls.add(u'张国荣')
        return pr
            
        
    @classmethod
    def step(cls):
        pr = cls.get_person_not_updated()
        if pr is None:
            return False
        print "Updating:", pr.zwm
        cls.update(pr.zwm)
        return True
# encoding: utf-8
from __future__ import unicode_literals

from django.db import models

from collection.models import PersonRecord
from dcxj.tool_env import CmdProgress


# Create your models here.
class Element(models.Model):
    name = models.CharField(max_length=100, verbose_name=u'中文名')
    type = models.PositiveSmallIntegerField(default=1, choices=((1,u"主语"),(2,u"谓语")), verbose_name=u'词性')


    class Meta:
        unique_together = [
            ("name", "type"),
        ]
        index_together = [
            ("name", "type"),    
                          ]


    def __unicode__(self):
        return '%s<%d>' % (self.name, self.type)

    
class Relation(models.Model):
    sub = models.ForeignKey(Element,related_name='sub', verbose_name=u'主')
    pred = models.ForeignKey(Element,related_name='pred', verbose_name=u'谓')
    obj = models.ForeignKey(Element,related_name='obj', verbose_name=u'宾')
    tag = models.BooleanField(default=True, verbose_name=u'是否成立')
    
    class Meta:
        unique_together = [
            ("sub", "pred", "obj", "tag"),
        ]
        index_together = [
            ("sub", "pred", "obj", "tag"),    
                          ]
    
    
    @classmethod
    def test(cls):
        q = PersonRecord.objects.filter(bd_index__gt=20000).order_by('bd_index')
        
        pred, _ = Element.objects.get_or_create(name=u'是', type=2)
        obj, _ = Element.objects.get_or_create(name=u'人', type=1)
        cp = CmdProgress(q.count())
        for x in q.iterator():
            sub, _ = Element.objects.get_or_create(name=x.zwm_clean, type=1)
            cls.objects.get_or_create(sub=sub, pred=pred, obj=obj, tag=1)
            cp.update()
        
    
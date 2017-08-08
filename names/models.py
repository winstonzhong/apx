# encoding: utf-8
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class Names(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    hid = models.IntegerField()
    eid = models.IntegerField()
    abandoned = models.BooleanField(default=False)
    
    class Meta:
        unique_together = [
            ("name", 'title'),
        ]
        index_together = [
            ("name", 'title'),    
                          ]

    def is_abandoned(self):
        from collection.models import HtmlContent, NameEntity
        hc = HtmlContent.objects.get(id=self.hid)
        ne = NameEntity(html=hc, eid=self.eid)
        self.abandoned = ne.predict() != 1
        self.save()
    
    @classmethod
    def predict_all(cls):
        for x in cls.objects.all().iterator():
            x.is_abandoned()
    
    def tinfo(self):
        from collection.models import HtmlContent
        hc = HtmlContent.objects.get(id=self.hid)
#         ne = NameEntity(html_id=self.hid, eid=self.eid)
        return hc.tinfo()
    tinfo.allow_tags = True
    tinfo.short_description = u'页面测试'

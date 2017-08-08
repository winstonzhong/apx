# encoding: utf-8
from __future__ import unicode_literals

import base64
import json
import re
import urlparse
import zlib

from django.db import models
from django.db.models.aggregates import Sum, Avg, Min, Max, Count
from django.db.models.expressions import F
from django.db.models.query_utils import Q
from django.db.transaction import atomic
from django.utils.functional import cached_property
import numpy
from pyquery.pyquery import PyQuery

from collection.tool_net import get_name_properties, get_index, \
    NoTableFoundError, NoPropertiesError, DumpPropertyError, JBQMNameParseError, \
    get_name_info, CODE_OTHER_EXCEPTIONS, get_english_info
from dcxj.base import get_dns_dict
from dcxj.tool_env import CmdProgress
from names.models import Names
from training.helper import local_single_redindex_train_svm
from utils.adv_ligament import AdvancedLigament
from utils.tool_env import force_utf8, force_unicode, split_english_words, \
    is_chinese
from utils.tool_html import remove_garbages
from utils.urlopen import urlopen, PageNotFound404, HtmlMalFormed, HTTP403


class Link(object):
    def __init__(self, src, refer):
        self.src = src
        self.refer = refer
    @property
    def url(self):
        return urlparse.urljoin(self.refer, self.src)
    
    @property
    def domain(self):
        return urlparse.urlparse(self.url).netloc
    
    @property
    def bad(self):
        if not self.domain.strip():
            return True
        return Site.objects.filter(domain=self.domain).first() is None

class Site(models.Model):
    domain = models.CharField(max_length=200, primary_key=True)
    url = models.URLField()
    
    @classmethod
    def add(cls, url):
        cls.objects.get_or_create(domain=urlparse.urlparse(url).netloc, defaults={'url':url})
        

class HtmlContent(models.Model):
    url = models.URLField()
    html = models.TextField(null=True, blank=True)
    corrupted = models.PositiveSmallIntegerField(default=0)
    has_names = models.NullBooleanField(null=True, blank=True)
    exported = models.BooleanField(default=False)
    class Meta:
        unique_together = [
            ("url", ),
        ]
        index_together = [
            ("url",),    
                          ]
    
    
    def tinfo(self):
        url = 'http://localhost:8081/%s/%d/' % (self.__class__.__name__.lower(), self.id)
        names_url = 'http://localhost:8081/admin/collection/nameentity/?html_id=%d' % self.id
#         url = 
        return u"<a href='%s' target=blank>%s</a> <br/> <a href='%s' target=blank>names</a>" % (url, self.url, names_url)
    tinfo.allow_tags = True
    tinfo.short_description = u'页面测试'
    
    
    @classmethod
    def all_need_to_be_crawled(cls):
        domains = map(lambda x:x.domain, Site.objects.all())
        while 1:
            empty = 0
            for domain in domains:
                r = cls.objects.filter(html=None, corrupted=0, url__icontains=domain).first()
                if r is not None:
                    empty = 1
                    yield r
            if not empty:
                break
                 

    @classmethod
    def crawl_all(cls):
        cnt = 1
        for r in cls.all_need_to_be_crawled():
            print "[%d] Updating:" % cnt, r.url
            r = cls.update_or_create(r.url)
            if not r.corrupted:
                r.crawl()
            cnt += 1
    
    @classmethod
    def old_crawl_all(cls):
        r = cls.objects.filter(html=None, corrupted=False).first()
        cnt = 1
        while r is not None:
            print "[%d] Updating:" % cnt, r.url
            r = cls.update_or_create(r.url)
            if not r.corrupted:
                r.crawl()
            r = cls.objects.filter(html=None, corrupted=False).first()
            cnt += 1
#             break
    
    def crawl(self):
        d = PyQuery(self.html)
        r = filter(lambda x:x.attrib.has_key('href'), d('a'))
        links = map(lambda x:Link(x.attrib['href'], self.url), r)
        
        @atomic(using='default', savepoint=True)
        def _run():
            print "Create Urls[%d]..." % len(links)
            cp = CmdProgress(len(links))
            for l in links:
                if not l.bad:
                    HtmlContent.objects.get_or_create(url=l.url)
                cp.update()
        _run()

        
        
    
    @classmethod
    def download(cls, url):
        html = urlopen(url, timeout=20)
        html = force_unicode(html)
        html = remove_garbages(html)
        body = PyQuery(html)('body')
        if not body:
            raise HtmlMalFormed
        
        def add_jbid(x, eid=0):
            children = PyQuery(x).children()
            for y in children:
                eid = add_jbid(y, eid)
            eid += 1
            try:
                x.attrib['jbid'] = str(eid)
            except:
                pass
            return eid
#         print html
#         print "body", body.text()
        add_jbid(body[0], 0)
        return body.html()
    
    @classmethod
    def get_or_create(cls, url):
        html = cls.download(url)
        return cls.objects.get_or_create(url=url, defaults={'html':html})[0]

    @classmethod
    def update_or_create(cls, url):
        try:
            html = cls.download(url)
            corrupted = 0
        except (PageNotFound404, HtmlMalFormed, HTTP403) as e:
            html = None
            corrupted = e.eid
            
        defaults={'html':html,
                  'corrupted':corrupted,
                  }
        return cls.objects.update_or_create(url=url, defaults=defaults)[0]

    
    def all_jbids(self):
        d = PyQuery(self.html)
        return map(lambda x:x.attrib.get('jbid'), d('[jbid]'))
#         for x in d.items('[jbid]'):
    
#     def get_title_and_names(self):
#         ids = self.all_jbids()
    @property
    def title_id(self):
        ids = self.all_jbids()
        for eid in ids:
            if TitleEntity(html=self, eid=int(eid)).predict() == 1:
                return eid
    @property
    def title(self):
        return PyQuery(self.html)('[jbid="%s"]' % self.title_id).text()
    
    @property
    def name_ids(self):
        return filter(lambda x:int(NameEntity(html=self, eid=int(x)).predict()) == 1, self.all_jbids())
    
    
    def set_names_as_trainee(self, label):
        ids = self.name_ids
        @atomic(using='default', savepoint=True)
        def _run():
            cp = CmdProgress(len(ids))
            for eid in ids:
                NameEntity.objects.update_or_create(html=self, eid=eid, defaults={'trainee':1, 'label':label})
                cp.update()
        _run()
        
    
    @property
    def names(self):
        return map(lambda x:PyQuery(self.html)('[jbid="%s"]' % x).text(), self.name_ids)
    
    def predict(self):
        ids = self.all_jbids()
        for eid in ids:
            if int(NameEntity(html=self, eid=int(eid)).predict()) == 1:
                return True
        return False
    
    @classmethod
    def export_all(cls):
        q = cls.objects.filter(~Q(html=None), corrupted=0, url__endswith='.html')
        for hc in q.iterator():
            ids = hc.name_ids
            hc.has_names = len(ids) > 0
            title = hc.title if hc.has_names else None
            for x in ids:
                name = PyQuery(hc.html)('[jbid="%s"]' % x).text()
                Names.objects.get_or_create(name=name, title=title, defaults={"hid":hc.id, "eid":x})
            hc.exported = True
            hc.save()
    
    @classmethod
    def predict_all(cls):
        q = cls.objects.filter(~Q(html=None), has_names=None, corrupted=0, url__endswith='.html')
#         @atomic(using='default', savepoint=True)
        def _run():
            cp = CmdProgress(q.count())
            for h in q.iterator():
                h.has_names =  h.predict()
                h.save() 
                cp.update()
        _run()
    
    def __unicode__(self):
        return self.url            
    
    def not_crawled(self):
        return self.html is None
    not_crawled.boolean = True

    def crawled(self):
        return self.html is not None
    crawled.boolean = True

class EntityBase(AdvancedLigament):
    features = (get_dns_dict,
                ) 
    
    @classmethod
    def create_all(cls):
        for html in HtmlContent.objects.all():
            cls.create(html=html) 
    
    @classmethod
    def create(cls, url=None, html=None):
        if url is not None and html is None:
            html = HtmlContent.get_or_create(url)
        assert html is not None
        
        ids = html.all_jbids()
        @atomic(using='default', savepoint=True)
        def _run():
            print "Create Title Entites..."
            cp = CmdProgress(len(ids))
            for eid in ids:
                cls.objects.get_or_create(html=html, eid=eid)
                cp.update()
        _run()

    def tinfo(self):
        url = 'http://localhost:8081/%s/%d/' % (self.__class__.__name__.lower(), self.id)
        html_url = 'http://localhost:8081/admin/collection/htmlcontent/?id=%d' % self.html.id
        
        return u"<a href='%s' target=blank>%.15s</a> <br/> <a href='%s'>HtmlContent</a>" % (url, self.element.text() or 'nan', html_url)
    tinfo.allow_tags = True
    tinfo.short_description = u'页面测试'
        
    @cached_property
    def element(self):
        return PyQuery(self.html.html)('[jbid="%d"]' % self.eid)
    
    @property
    def tag(self):
        return self.element[0].tag
    
    @property
    def text(self):
        return self.element.text()
    
    @property
    def CHINESE_CNT(self):
        return len(filter(lambda x:is_chinese(x), self.text))

    @property
    def CC_LTE4(self):
        return self.CHINESE_CNT <=4
    
    def get_record(self):
        return self

    @classmethod
    def get_dna_fields(cls):
        return cls.dna_fields

    @classmethod
    def train(cls):
        local_single_redindex_train_svm(cls)

    @classmethod
    def update_pval(cls, q):
        return#这里不需要进行排序
    
    @classmethod
    def test(cls):
        cls.train()
        cls.reload_model()
        cls.predict_all(cls.objects.all())

        
class TitleEntity(EntityBase, models.Model):
    html = models.ForeignKey(HtmlContent)
    
    eid = models.IntegerField()
    
    trainee = models.BooleanField(default=False)
    
    testee = models.BooleanField(default=False)
    
    label = models.SmallIntegerField(default=0)
    
    result = models.SmallIntegerField(blank=True, null=True)
    
    pval =  models.FloatField(blank=True, null=True)
    
    weight = models.PositiveSmallIntegerField(default=1)
    
    memo = models.TextField(null=True, blank=True)
 
    dna_fields = [
                'IS_TAG_H',
                'CHINESE_CNT',
#                 'CC_LTE4',
                  ] 

    class Meta:
        unique_together = [
            ("html", "eid"),
        ]
        index_together = [
            ("html", "eid"),    
                          ]


    datfile = "jb_title.dat"
    svm_model = None
    ranges = None
    dna = None
    abd_dnas = None

    
    @property
    def IS_TAG_H(self):
        return self.tag.lower().startswith('h')

class NameEntity(EntityBase, models.Model):
    html = models.ForeignKey(HtmlContent)
    
    eid = models.IntegerField()
    
    trainee = models.BooleanField(default=False)
    
    testee = models.BooleanField(default=False)
    
    label = models.SmallIntegerField(default=0)
    
    result = models.SmallIntegerField(blank=True, null=True)
    
    pval =  models.FloatField(blank=True, null=True)
    
    weight = models.PositiveSmallIntegerField(default=1)
    
    memo = models.TextField(null=True, blank=True)
 
    dna_fields = [
#                 'IS_TAG_H',
                'CHINESE_CNT',
                'ST_SIB_CNT',
                'SIB_RATE',
                'TEXT_DENS',
#                 'PARENT_TD',
                'A_CNT',
                'HTML_CNT',
                'SIBS_TEXT_CNT_MEAN',
#                 'CC_LTE4',
                  ] 

    class Meta:
        unique_together = [
            ("html", "eid"),
        ]
        index_together = [
            ("html", "eid"),    
                          ]


    datfile = "jb_name.dat"
    svm_model = None
    ranges = None
    dna = None
    abd_dnas = None
    
    @property
    def HTML_CNT(self):
        return len(self.element.outer_html())
    @property
    def A_CNT(self):
        return len(self.element('a'))
    @property
    def TEXT_DENS(self):
        return len(self.element.text()) * 1.0 / len(self.element.outer_html())

    @property
    def PARENT_TD(self):
        p = self.element.parent()
        return len(p.text()) * 1.0 / len(p.outer_html())
    
    @property
    def ST_SIB_CNT(self):
        return len(self.element.siblings(self.tag))

    @property
    def SIB_RATE(self):
        total = len(self.element.siblings())
        return self.ST_SIB_CNT * 1.0 / total if total else 0
    
    @property
    def SIBS_TEXT_CNT_MEAN(self):
        r = map(lambda x:len(PyQuery(x).text()), self.element.siblings())
        return numpy.mean(r) if r else 9
    
    
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
# encoding: utf-8
from django.contrib import admin
from django.db.models.expressions import F
from django.db.models.query_utils import Q

from autobatch.django_actions import toggle_trainee, set_fake, set_label_1, \
    set_label_n1
from collection.models import PersonRecord, CommonEnglishNames, HtmlContent, \
    TitleEntity, NameEntity, Site


class TrainingListFilter(admin.SimpleListFilter):
    title = u'培训结果'

    parameter_name = 'selftest_result'

    def lookups(self, request, model_admin):
        return (
            ('1', u'成功记录'),
            ('0', u'失败的记录'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(Q(result=F("label")))
        if self.value() == '0':
            return queryset.filter(~Q(result=F("label")))

class TitleHnFilter(admin.SimpleListFilter):
    title = u'tag是h'

    parameter_name = '_hn'

    def lookups(self, request, model_admin):
        return (
            ('1', u'hx'),
#             ('0', u'失败的记录'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            r = filter(lambda x:x.IS_TAG_H, queryset)
            return queryset.filter(id__in=map(lambda x:x.id, r))

class HtmlEmptyFilter(admin.SimpleListFilter):
    title = u'内容空'

    parameter_name = '_html_empty'

    def lookups(self, request, model_admin):
        return (
            ('1', u'为空'),
            ('-1', u'不为空'),
#             ('0', u'失败的记录'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(html=None)

        if self.value() == '-1':
            return queryset.filter(~Q(html=None))

class SibCntFilter(admin.SimpleListFilter):
    title = u'同样Tag的邻居 个数排序'

    parameter_name = '_sibcnt'

    def lookups(self, request, model_admin):
        return (
            ('1', u'最大前100'),
            ('-1', u'最小前100'),
#             ('-1', u'后100'),
#             ('0', u'失败的记录'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            records = map(lambda x:x, queryset)
            records.sort(key=lambda x:-x.ST_SIB_CNT)
            return queryset.filter(id__in=map(lambda x:x.id, records[:100]))

        if self.value() == '-1':
            records = map(lambda x:x, queryset)
            records.sort(key=lambda x:x.ST_SIB_CNT)
            return queryset.filter(id__in=map(lambda x:x.id, records[:100]))

@admin.register(PersonRecord)
class PersonRecordAdmin(admin.ModelAdmin):
    list_display = ['zwm', 'tinfo', 'ywm', 'xb', 'sg', 'tz', 'xx', 'csny','qsny', 'xz', 'zy', 'cddq', 'gj','bd_index', 'name_shuli', 'updated']



@admin.register(CommonEnglishNames)
class CommonEnglishNamesAdmin(admin.ModelAdmin):
    list_display = ['name', 'sex', 'sex_count']


def set_all_names_as_trainee_n1(modeladmin, request, queryset):
    for hc in queryset.iterator():
        hc.set_names_as_trainee(-1)
set_all_names_as_trainee_n1.short_description = u"将所有的names记录设为---1培训记录"

def set_all_names_as_trainee_1(modeladmin, request, queryset):
    for hc in queryset.iterator():
        hc.set_names_as_trainee(1)
set_all_names_as_trainee_1.short_description = u"将所有的names记录设为+++1培训记录"



@admin.register(HtmlContent)
class HtmlContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'tinfo', 'crawled', 'corrupted', 'has_names', 'exported']
    
    list_filter = ('corrupted',HtmlEmptyFilter,'has_names')

    actions = [
        set_all_names_as_trainee_1,
        set_all_names_as_trainee_n1,
               ]


@admin.register(TitleEntity)
class TitleEntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'tinfo', 'eid', 'trainee', 'label', 'result'] + TitleEntity.dna_fields
    list_filter = (
                   'label', 
                    'trainee', 
                    'result',
                    TrainingListFilter,
                    TitleHnFilter,
                       )
    actions = [
               toggle_trainee,
               set_label_1,
               set_label_n1,
               ]

@admin.register(NameEntity)
class NameEntityAdmin(admin.ModelAdmin):
    list_display = ['id', 'tinfo', 'eid', 'trainee', 'label', 'result'] + NameEntity.dna_fields
    list_filter = (
                   'label', 
                    'trainee', 
                    'result',
                    TrainingListFilter,
                    SibCntFilter,
                       )
    actions = [
               toggle_trainee,
               set_label_1,
               set_label_n1,
               ]


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['domain', 'url']

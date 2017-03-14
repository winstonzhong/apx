from django.contrib import admin

from collection.models import PersonRecord, CommonEnglishNames


# Register your models here.
@admin.register(PersonRecord)
class PersonRecordAdmin(admin.ModelAdmin):
    list_display = ['zwm', 'tinfo', 'ywm', 'xb', 'sg', 'tz', 'xx', 'csny','qsny', 'xz', 'zy', 'cddq', 'gj','bd_index', 'name_shuli', 'updated']



@admin.register(CommonEnglishNames)
class CommonEnglishNamesAdmin(admin.ModelAdmin):
    list_display = ['name', 'sex', 'sex_count']

from django.contrib import admin
from collection.models import PersonRecord

# Register your models here.
@admin.register(PersonRecord)
class PersonRecordAdmin(admin.ModelAdmin):
    list_display = ['zwm', 'tinfo', 'ywm', 'xb', 'sg', 'tz', 'xx', 'csny','qsny', 'xz', 'zy', 'cddq', 'bd_index', 'updated']



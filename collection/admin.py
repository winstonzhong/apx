from django.contrib import admin
from collection.models import PersonRecord

# Register your models here.
@admin.register(PersonRecord)
class PersonRecordAdmin(admin.ModelAdmin):
    list_display = ['zwm', 'ywm', 'xb', 'sg', 'tz', 'xx', 'csny', 'xz', 'bd_index']



from django.contrib import admin

from names.models import Names


# Register your models here.
@admin.register(Names)
class NamesAdmin(admin.ModelAdmin):
    list_display = ['id', 'tinfo', 'name', 'title']
    
#     list_filter = ('corrupted',HtmlEmptyFilter,)

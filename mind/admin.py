from django.contrib import admin
from mind.models import Relation, Element

# Register your models here.

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'type']


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ['sub', 'pred', 'obj', 'tag']

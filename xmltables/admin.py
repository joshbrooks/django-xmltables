from django.contrib import admin

# Register your models here.

from .models import XmlColumn, XmlNamespace, XmlTable

@admin.register(XmlColumn, XmlNamespace, XmlTable)
class XmlTableAdmin(admin.ModelAdmin):
    pass

from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from . import models as xmltables


class XmlTableList(ListView):
    model = xmltables.XmlTable


class XmlTableDetail(DetailView):
    context_object_name = "xmltable"
    queryset = xmltables.XmlTable.objects.all()

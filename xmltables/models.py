
from django.db import models

class XmlField(models.TextField):

    description = "An XML type field"

    def __init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'xml'

    def get_internal_type(self):
        return 'XML'


class XmlBaseModel(models.Model):
    content = XmlField()

    class Meta:
        abstract = True



class XmlColumn(models.Model):
    col_name = models.CharField(max_length=256)
    col_type = models.CharField(max_length=256, default="text")
    column_expression = models.CharField(max_length=256, null=True, blank=True)
    default_expression = models.CharField(max_length=256, null=True, blank=True)
    not_null = models.BooleanField(default=False)
    for_ordinality = models.BooleanField(default=False)

    @property
    def sql(self):
        entries = [
            self.col_name,
            self.col_type if not self.for_ordinality else False,
            f"PATH '{self.column_expression}'" if self.column_expression else False,
            f"DEFAULT {self.default_expression}" if self.default_expression else False,
            "NOT NULL" if self.not_null else False,
            "FOR ORDINALITY" if self.for_ordinality else False,
        ]
        return " ".join([e for e in entries if e])



class XmlNamespace(models.Model):
    uri = models.CharField(max_length=256)
    name = models.CharField(max_length=256)

    @property
    def sql(self):
        return f"'{self.namespace_uri}' AS \"{self.namespace_name}\""


class XmlTable(models.Model):
    document_expression = models.CharField(max_length=256)
    row_expression = models.CharField(max_length=256)
    namespaces = models.ManyToManyField(XmlNamespace)
    columns = models.ManyToManyField(XmlColumn)

    @property
    def __namespaces(self):
        if self.namespaces:
            return "XMLNAMESPACES({}),".format(
                ", ".join(ns.sql for ns in self.namespaces)
            )
        return ""

    @property
    def __columns(self):
        if self.columns:
            return "{}".format(", ".join(ns.sql for ns in self.columns))
        return ""

    @property
    def sql(self):
        return f"XMLTABLE({self.__namespaces}'{self.document_expression}' PASSING {self.row_expression} COLUMNS {self.__columns})"


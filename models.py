
from django.db import models
from django.db import connection
from django.utils.text import slugify
import logging
logger = logging.getLogger(__name__)

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
    col_xsd_type = models.CharField(max_length=256, default="xsd:string")
    column_expression = models.CharField(max_length=256, null=True, blank=True)
    default_expression = models.CharField(max_length=256, null=True, blank=True)
    not_null = models.BooleanField(default=False)
    for_ordinality = models.BooleanField(default=False)

    @property
    def sql_parts(self):
        return [
            self.col_name,
            self.col_type.upper() if not self.for_ordinality else False,
            f"PATH '{self.column_expression}'" if self.column_expression else False,
            f"DEFAULT {self.default_expression}" if self.default_expression else False,
            "NOT NULL" if self.not_null else False,
            "FOR ORDINALITY" if self.for_ordinality else False,
        ]

    @property
    def sql(self):
        return " ".join([e for e in self.sql_parts if e])

    def __str__(self):
        return self.sql

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
        if self.namespaces.count():
            return "XMLNAMESPACES({}),".format(
                ", ".join(ns.sql for ns in self.namespaces.all())
            )
        return ""

    @property
    def __columns(self):
        if self.columns:
            return "{}".format("    ,\n".join(ns.sql for ns in self.columns.all()))
        return ""

    @property
    def sql(self):
        return f"""
XMLTABLE({self.__namespaces}'{self.row_expression}' 
    PASSING {self.document_expression} 
    COLUMNS {self.__columns})"""

    def execute(self):
        with connection.cursor() as c:
            c.execute(self.sql)
            return c.fetchall()

    def materialize(self):
        from django.db import connection
        name = slugify(self.row_expression.replace('-', '_'))
        with connection.cursor() as c:
            c.execute(f'DROP MATERIALIZED VIEW IF EXISTS "{name}" CASCADE')
            try:
                c.execute(f'CREATE MATERIALIZED VIEW "{name}" AS {self.sql}')
            except Exception as e:
                logger.error(f'''Unable to continue; SQL was {self.sql}''', exc_info=1) 
                raise
    
    def __str__(self):
        return self.row_expression
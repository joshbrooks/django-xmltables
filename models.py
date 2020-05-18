from django.db import models
from django.db import connection
from django.utils.text import slugify
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


class XmlField(models.TextField):

    description = "An XML type field"

    def db_type(self, connection):
        return "xml"

    def get_internal_type(self):
        return "XML"


class XmlColumn(models.Model):
    """
    Generates the XML required to return a "column_expression"
    from an XMLTABLE expression
    """
    col_name = models.CharField(max_length=256)
    col_type = models.CharField(max_length=256, default="text")
    col_xsd_type = models.CharField(max_length=256, default="xsd:string")
    column_expression = models.CharField(max_length=256, null=True, blank=True)
    default_expression = models.CharField(max_length=256, null=True, blank=True)
    not_null = models.BooleanField(default=False)
    for_ordinality = models.BooleanField(default=False)

    @property
    def sql(self):
        return render_to_string('xmlcolumn.sql', dict(column=self))

    def __str__(self): 
        return self.col_name

class XmlNamespace(models.Model):
    uri = models.CharField(max_length=256)
    name = models.CharField(max_length=256)

    @property
    def sql(self):
        return render_to_string('xmlnamespace.sql', dict(namespace=self))

    def __str__(self):
        return self.name

class XmlTable(models.Model):
    document_expression = models.CharField(max_length=256)
    row_expression = models.CharField(max_length=256)
    namespaces = models.ManyToManyField(XmlNamespace)
    columns = models.ManyToManyField(XmlColumn)

    @property
    def sql(self):
        # hint: may pay to select_related() on namespaces and columns
        return render_to_string('xmltable.sql', dict(xmltable=self))

    def execute(self):
        """
        with connection.cursor() as c:
            c.execute(self.sql)
            return c.fetchall()
        """
        raise NotImplementedError("execute should be overridden by a subclass")

    def execute_with_columns(self):
        """
        with connection.cursor() as c:
            c.execute(self.sql)
            return [col[0] for col in c.description], c.fetchall()
        """
        raise NotImplementedError("execute_with_columns should be overridden by a subclass")

    def materialize(self):
        """
        from django.db import connection
        name = slugify(self.row_expression.replace('-', '_'))
        with connection.cursor() as c:
            c.execute(f'DROP MATERIALIZED VIEW IF EXISTS "{name}" CASCADE')
            try:
                c.execute(f'CREATE MATERIALIZED VIEW "{name}" AS (SELECT * FROM {self.sql})')
            except Exception as e:
                logger.error(f'''Unable to continue; SQL was {self.sql}''', exc_info=1) 
                raise
        """
        raise NotImplementedError("materialize should be overridden by a subclass")

    def __str__(self):
        return self.row_expression

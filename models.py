from typing import Any, Optional
from django.db import models
from django.db import connection
from django.utils.text import slugify
from django.template.loader import render_to_string
import logging
from psycopg2 import sql

logger = logging.getLogger(__name__)


class XmlField(models.TextField):

    description = "An XML type field"

    def db_type(self, connection):
        return "xml"

    def get_internal_type(self):
        return "XML"


class ColumnQuerySet(models.QuerySet):
    def render(self):
        parts = sql.SQL("COLUMNS ")
        first_column = True

        for column in self:
            if not first_column:
                parts += sql.SQL(",")
            first_column = False
            parts += column.render()  # type: ignore

        return parts


class ColumnManager(models.Manager):
    def get_queryset(self):
        return ColumnQuerySet(self.model, using=self._db)


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

    objects = ColumnManager()

    def render(self) -> sql.Composable:
        parts = sql.Identifier(self.col_name)
        if not self.for_ordinality:
            parts += sql.SQL(self.col_type)
            if self.column_expression:
                parts += sql.SQL("PATH")
                parts += sql.Literal(self.column_expression)
        if self.default_expression:
            parts += sql.SQL("DEFAULT")
            parts += sql.Literal(self.default_expression)
        if self.not_null:
            parts += sql.SQL("NOT NULL")
        if self.for_ordinality:
            parts += sql.SQL("FOR ORDINALITY")
        return sql.SQL(" ").join(parts)

    @property
    def sql(self):
        return "{}".format(self.render())

    def __str__(self):
        return f"{self.col_name} (from) {self.column_expression}"


class XmlNamespace(models.Model):
    uri = models.CharField(max_length=256)
    name = models.CharField(max_length=256)

    @property
    def sql(self):
        return render_to_string("xmlnamespace.sql", dict(namespace=self))

    def __str__(self):
        return self.name


from django.contrib.contenttypes.models import ContentType


class XmlTable(models.Model):
    document_expression = models.CharField(
        max_length=256,
        help_text="Provide context for the XMLTABLE query. This will likely be the name of the XML type column or a path to derive data from that column.",
    )
    row_expression = models.CharField(max_length=256)
    namespaces = models.ManyToManyField(XmlNamespace)
    columns = models.ManyToManyField(XmlColumn)
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Determine which model the XMLTABLE query would refer to",
    )

    def render(self) -> sql.Composable:
        return sql.SQL(
            "XMLTABLE({row_expression} PASSING {doc_expression} {columns})"
        ).format(
            # namespaces=self.namespaces.render(),
            row_expression=sql.Literal(self.row_expression),
            doc_expression=sql.SQL(self.document_expression),
            columns=self.columns.all().render(),
        )

    def select_query(self, source) -> sql.Composable:
        return sql.SQL("SELECT {fields} FROM {source}, {xmltable}").format(
            fields=sql.SQL("xmltable.*"),
            source=sql.SQL(source),
            xmltable=self.render(),
        )

    @property
    def sql(self):
        # hint: may pay to select_related() on namespaces and columns
        return render_to_string("xmltable.sql", dict(xmltable=self))

    def execute(self, cur: Any = None):

        source = self.content_type.model_class()._meta.db_table
        if cur:
            cur.execute(self.select_query(source))
            return cur.fetchall()
        with connection.cursor() as cur:
            cur.execute(self.select_query(source))
            return cur.fetchall()

    def execute_with_columns(self):
        """
        with connection.cursor() as c:
            c.execute(self.sql)
            return [col[0] for col in c.description], c.fetchall()
        """
        raise NotImplementedError(
            "execute_with_columns should be overridden by a subclass"
        )

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

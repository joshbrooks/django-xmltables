XMLTABLE(
    {% include 'xmlnamespace_set.sql' with namespaces=xmltable.namespaces.all %}
    '{{xmltable.row_expression|safe}}' PASSING {{xmltable.document_expression|safe}}
    {% include 'xmlcolumn_set.sql' with columns=xmltable.columns.all %}
)
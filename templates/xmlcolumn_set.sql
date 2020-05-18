{% if columns %}
COLUMNS {% for column in columns %}
    {% include 'xmlcolumn.sql' with column=column %}{% if not forloop.last %},{% endif %}{% endfor %}
{% endif %}
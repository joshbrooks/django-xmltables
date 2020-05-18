{% if not namespaces %}{% else %}
    XMLNAMESPACES({% for namespace in namespaces %}
        {% include 'xmlnamespace.sql' with column=column %}{% if not forloop.last %},{% endif %}{% endfor %}
    ){% endif %}

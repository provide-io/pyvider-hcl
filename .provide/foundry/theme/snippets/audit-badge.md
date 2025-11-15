<!-- Audit Badge - Compact inline indicator -->
{% set page_meta = page.meta or {} %}
{% set is_audited = page_meta.get('audited', false) %}
{% if is_audited %}:white_check_mark:{ title="Human Reviewed" } **Reviewed**{% else %}:robot:{ title="AI-Generated" } **AI-Generated**{% endif %}

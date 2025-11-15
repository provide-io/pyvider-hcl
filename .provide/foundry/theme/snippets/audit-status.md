<!-- Audit Status Snippet - Include at top of pages to show review status -->

{% set page_meta = page.meta or {} %}
{% set is_audited = page_meta.get('audited', false) %}
{% set reviewer = page_meta.get('reviewer', '') %}
{% set audit_notes = page_meta.get('audit_notes', '') %}
{% set audit_date = page_meta.get('audit_date', '') %}

{% if is_audited %}
!!! success "Human Reviewed"
    **Status:** ✅ This page has been reviewed and approved by a human.
    {% if reviewer %}

    **Reviewer:** {{ reviewer }}
    {% endif %}
    {% if audit_date %}

    **Date:** {{ audit_date }}
    {% endif %}
    {% if audit_notes %}

    **Notes:** {{ audit_notes }}
    {% endif %}
{% else %}
!!! warning "AI-Generated Content"
    **Status:** 🤖 This page contains AI-generated content that has not been reviewed by a human.

    Please verify information independently and [report issues]({{ config.repo_url }}/issues) if you find inaccuracies.
{% endif %}

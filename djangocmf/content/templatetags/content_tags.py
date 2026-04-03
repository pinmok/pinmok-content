#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content_tags module

Description:
  
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/3/25
"""
from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from djangocmf.content.enums import ArticleStatus

register = template.Library()


@register.simple_tag
def ribbon(status: str):
    """Return a Bootstrap ribbon HTML representing the article status."""
    status_map = {
        ArticleStatus.DRAFT: ('bg-success', ArticleStatus.DRAFT.label),
        ArticleStatus.PENDING: ('bg-warning', ArticleStatus.PENDING.label),
        ArticleStatus.RETURNED: ('bg-danger', ArticleStatus.RETURNED.label),
        ArticleStatus.PUBLISHED: ('bg-primary', ArticleStatus.PUBLISHED.label),
        ArticleStatus.DELETED: ('bg-dark', ArticleStatus.DELETED.label),
    }

    # normalize → try convert to enum
    try:
        status_enum = ArticleStatus(status)
    except (ValueError, TypeError):
        status_enum = None

    # fallback
    if status_enum not in status_map:
        css_class = 'bg-secondary'
        label = _('New Article')
    else:
        css_class, label = status_map[status_enum]

    return mark_safe(f'<div class="ribbon {css_class}">{label}</div>')

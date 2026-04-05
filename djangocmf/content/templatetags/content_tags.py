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
    try:
        status_enum = ArticleStatus(status)
        css_class = f'bg-{status_enum.color}'
        label = status_enum.label
    except (ValueError, TypeError):
        css_class = 'bg-secondary'
        label = _('New Article')

    return mark_safe(f'<div class="ribbon {css_class}">{label}</div>')

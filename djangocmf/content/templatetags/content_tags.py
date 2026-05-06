#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content_tags module

Description:
  Template tags for the content app.
  Load in templates with: {% load content_tags %}
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/3/25
"""
from uuid import UUID

from django import template
from django.core.exceptions import ValidationError
from django.core.paginator import Page
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from djangocmf.content.enums import ArticleStatus
from djangocmf.content.models import Article, Category
from djangocmf.content.service.frontend import ArticleFrontendService, CategoryFrontendService
from project_settings import settings

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
        label = _('New')

    return mark_safe(f'<div class="ribbon {css_class}">{label}</div>')


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

VALID_ORDER_FIELDS = {
    'published_at', '-published_at',
    'created_at', '-created_at',
    'sort_order', '-sort_order',
}


@register.simple_tag(name='articles')
def articles_tag(
        category: str | list,
        page_num: int = 1,
        page_size: int = 10,
        limit: int | None = None,
        order: str = '-published_at',
        top: bool = False,
        recommended: bool = False,
) -> Page | list:
    """
    Return a paginated Page object or a plain list of published articles.

    Args:
        category:    Category UUID to filter by. Pass None for all categories.
        page_num:    Page number (1-based). Ignored when limit is set.
        page_size:   Number of articles per page. Ignored when limit is set.
        limit:       If set, disables pagination and returns a plain list of at most N articles.
        order:       Sort field. Must be one of: published_at, -published_at, created_at,
                     -created_at, sort_order, -sort_order. Invalid values fall back to -published_at.
        top:         If True, return only is_top articles.
        recommended: If True, return only is_recommended articles.

    Usage:
        {% articles limit=6 as latest %}
        {% articles limit=4 order='sort_order' as ordered %}
        {% articles category=uuid page_num=current_page page_size=10 as paged %}
        {% articles top=True limit=2 as top_articles %}
    """
    if order not in VALID_ORDER_FIELDS:
        order = '-published_at'

    if limit is not None:
        articles = ArticleFrontendService.get_article_list(
            category=category,
            limit=int(limit),
            order_by=order.split(','),
            top_only=top,
            recommended_only=recommended,
        )
        return articles

    return ArticleFrontendService.get_article_list(
        category=category,
        page_number=page_num,
        page_size=int(page_size),
        order_by=order.split(','),
        top_only=top,
        recommended_only=recommended,
    )


@register.simple_tag(name='article')
def article_tag(uuid: UUID) -> Article | None:
    """
    Return a single published article by UUID, or None if not found.

    Usage:
        {% article uuid=some_uuid as art %}
        {% if art %}
            {{ art.translation.title }}
        {% endif %}
    """
    try:
        return ArticleFrontendService.get_article_by_uuid(uuid)
    except ValidationError as e:
        if settings.DEBUG:
            raise e
        return None


@register.simple_tag(name='page')
def page_tag(uuid: UUID) -> Article | None:
    """
    Return a single published page by UUID, or None if not found.

    Usage:
        {% page uuid=some_uuid as pg %}
        {% if pg %}
            {{ pg.translation.title }}
        {% endif %}
    """
    try:
        return ArticleFrontendService.get_article_by_uuid(uuid)
    except ValidationError as e:
        if settings.DEBUG:
            raise e
        return None


@register.simple_tag(name='category')
def category_tag(uuid: UUID) -> Category | None:
    """
    Return a single active category by UUID, or None if not found.

    Usage:
        {% category uuid=some_uuid as cat %}
        {% if cat %}
            {{ cat.name }}
        {% endif %}
    """
    try:
        return CategoryFrontendService.get_category_by_uuid(uuid)
    except ValidationError as e:
        if settings.DEBUG:
            raise e
        return None


def _build_page_range(current_page: int, total_pages: int, wing_size: int) -> list[int | None]:
    """
    Build a page number sequence with None representing ellipsis positions.

    Always includes first and last page. Shows wing_size pages on each side
    of the current page. Gaps between window and first/last are filled with None.
    """
    if total_pages <= wing_size * 2 + 3:
        return list(range(1, total_pages + 1))

    left_bound = max(2, current_page - wing_size)
    right_bound = min(total_pages - 1, current_page + wing_size)

    result: list[int | None] = [1]

    if left_bound > 2:
        result.append(None)  # left ellipsis

    result.extend(range(left_bound, right_bound + 1))

    if right_bound < total_pages - 1:
        result.append(None)  # right ellipsis

    result.append(total_pages)
    return result


@register.inclusion_tag('content/tags/pagination.html')
def pagination_tag(
        page_obj: Page,
        wing: int = 4,
        ul_class: str = 'pagination',
        item_class: str = 'page-item',
        link_class: str = 'page-link',
        active_class: str = 'active',
        disabled_class: str = 'disabled',
        prev_label: str = '«',
        next_label: str = '»',
        ellipsis_text: str = '...',
) -> dict:
    """
    Render a pagination control for a Django Page object.

    Displays: « first ... [wing pages] [current] [wing pages] ... last »
    When the window is adjacent to first/last, ellipsis is suppressed.

    Args:
        page_obj:       Django Page instance, typically from {% articles %}.
        wing:           Number of pages to show on each side of current. Default 4.
        ul_class:       CSS class for the <ul> element.
        item_class:     CSS class for each <li> element.
        link_class:     CSS class for each <a> element.
        active_class:   Extra CSS class for the current page <li>.
        disabled_class: Extra CSS class for disabled prev/next <li>.
        prev_label:     Label for the previous page link.
        next_label:     Label for the next page link.
        ellipsis_text:  String displayed between gaps.

    Usage:
        {% pagination articles %}
        {% pagination articles wing=2 ul_class="pager" %}
    """
    if not isinstance(page_obj, Page):
        return {'show': False}

    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    page_range = _build_page_range(current_page, total_pages, wing)

    return {
        'show': total_pages > 1,
        'page_range': page_range,
        'current_page': current_page,
        'total_pages': total_pages,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'ul_class': ul_class,
        'item_class': item_class,
        'link_class': link_class,
        'active_class': active_class,
        'disabled_class': disabled_class,
        'prev_label': prev_label,
        'next_label': next_label,
        'ellipsis_text': ellipsis_text,
    }

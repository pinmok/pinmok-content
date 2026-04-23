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
from django import template
from django.core.paginator import Page
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from djangocmf.content.enums import ArticleStatus
from djangocmf.content.models import Article, Category
from djangocmf.content.service.frontend import ArticleFrontendService, CategoryFrontendService

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
# Internal helpers
# ---------------------------------------------------------------------------

def _get_translation(article):
    """
    Return the prefetched translation for an article if available,
    otherwise fall back to Article.get_translation().

    ArticleFrontendService._base_qs() prefetches translations into
    _current_translations. This helper uses that cache to avoid
    extra queries when iterating over article lists.
    """
    cached = getattr(article, '_current_translations', None)
    if cached is not None:
        return cached[0] if cached else None
    return article.get_translation()


def _attach_translation(article):
    """
    Attach a `translation` attribute directly onto the article instance
    so templates can use {{ article.translation.title }} uniformly,
    regardless of whether prefetch was used.
    """
    article.translation = _get_translation(article)
    return article


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

@register.simple_tag(name='articles')
def articles_tag(
        category: str | None = None,
        page_num: int = 1,
        limit: int = 10,
        top: bool = False,
        recommended: bool = False,
) -> Page:
    """
    Return a paginated Page object of published articles.

    Args:
        category:    Category UUID to filter by. Accepts a single UUID string.
                     Pass None to return articles from all categories.
        page_num:    Page number (1-based).
        limit:       Number of articles per page.
        top:         If truthy, return only is_top articles.
        recommended: If truthy, return only is_recommended articles.

    Usage:
        {% list as articles %}
        {% list category=cat_uuid page=current_page size=10 as articles %}
        {% for article in articles %}
            {{ article.translation.title }}
        {% endfor %}
    """
    category_uuids = [category] if isinstance(category, str) else category or None
    article_page = ArticleFrontendService.get_article_list(
        category_uuids=category_uuids,
        page_number=page_num,
        page_size=int(limit),
        top_only=top,
        recommended_only=recommended,
    )

    # Attach translation to each article to avoid per-item queries in templates
    for art in article_page.object_list:
        _attach_translation(art)

    return article_page


@register.simple_tag(name='article')
def article_tag(uuid: str) -> Article | None:
    """
    Return a single published article by UUID, or None if not found.

    Usage:
        {% article uuid=some_uuid as art %}
        {% if art %}
            {{ art.translation.title }}
        {% endif %}
    """
    art = ArticleFrontendService.get_article_by_uuid(uuid)
    if art:
        _attach_translation(art)
    return art


@register.simple_tag(name='page')
def page_tag(uuid: str) -> Article | None:
    """
    Return a single published page by UUID, or None if not found.

    Usage:
        {% page uuid=some_uuid as pg %}
        {% if pg %}
            {{ pg.translation.title }}
        {% endif %}
    """
    pg = ArticleFrontendService.get_page_by_uuid(uuid)
    if pg:
        _attach_translation(pg)
    return pg


@register.simple_tag(name='category')
def category_tag(uuid: str) -> Category | None:
    """
    Return a single active category by UUID, or None if not found.

    Usage:
        {% category uuid=some_uuid as cat %}
        {% if cat %}
            {{ cat.name }}
        {% endif %}
    """
    return CategoryFrontendService.get_category_by_uuid(uuid)


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

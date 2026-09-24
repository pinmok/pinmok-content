#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api module

Description:
  Read-only JSON API views for the content app.

  All endpoints return published/active content only.
  Authentication and rate-limiting are left to the project layer.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-07-04
"""
from uuid import UUID

from django.core.files.storage import default_storage
from django.http import HttpRequest
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET

from pinmok.content.enums import ArticleType
from pinmok.content.models import Article, Category
from pinmok.content.service.frontend import ArticleFrontendService, CategoryFrontendService
from pinmok.core.api import ErrorCode, error, success

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_ORDER_FIELDS = {
    'published_at', '-published_at',
    'created_at', '-created_at',
    'sort_order', '-sort_order',
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_url(field) -> str:
    """Return field.url safely, or '' if the file is missing or field is empty."""
    if not field:
        return ''

    try:
        # Case 1: Django's ImageField/FileField (FieldFile instance)
        # It has a 'field' attribute pointing to the Field definition
        # field.url already includes MEDIA_URL prefix
        if hasattr(field, 'field'):
            return field.url or ''

        # Case 2: Resource instance or plain string
        if hasattr(field, 'url'):
            path_val = field.url
        else:
            path_val = str(field)

        if not path_val:
            return ''

        # External full URL: return as-is
        if path_val.startswith(('http://', 'https://', '//')):
            return path_val

        # Relative path: resolve via storage backend (auto-prepend MEDIA_URL)
        return default_storage.url(path_val)
    except (ValueError, FileNotFoundError):
        return ''


# ---------------------------------------------------------------------------
# Serializers
# ---------------------------------------------------------------------------

def _serialize_category(cat: Category) -> dict:
    """Serialize a Category instance to a plain dict."""
    translation = cat.translation
    return {
        'uuid': str(cat.uuid),
        'name': translation.name if translation else '',
        'description': translation.description if translation else '',
        'cover': _safe_url(cat.cover),
        'parent': str(cat.parent.uuid) if cat.parent_id else None,
        'sort_order': cat.sort_order,
    }


def _serialize_article_summary(art: Article) -> dict:
    """Serialize an Article instance to a summary dict (for list views)."""
    translation = art.translation
    return {
        'uuid': str(art.uuid),
        'title': translation.title if translation else '',
        'summary': translation.summary if translation else '',
        'cover': _safe_url(art.cover),
        'is_top': art.is_top,
        'is_recommended': art.is_recommended,
        'published_at': art.published_at.isoformat() if art.published_at else None,
        'categories': [str(c.uuid) for c in art.categories.all()],
    }


def _serialize_article_detail(art: Article) -> dict:
    """Serialize an Article instance to a full detail dict."""
    translation = art.translation
    data = _serialize_article_summary(art)

    def _serialize_resources(usage_key: str) -> list:
        """Serialize a list of ArticleResource objects by usage type."""
        return [
            {
                'url': _safe_url(r.resource),
                'original_name': r.resource.original_name,
                'alt': r.alt,
            }
            for r in getattr(art, usage_key, [])
        ]

    data.update({
        'content': translation.content if translation else '',
        'gallery': _serialize_resources('gallery'),
        'attachments': _serialize_resources('attachments'),
        'videos': _serialize_resources('videos'),
        'audios': _serialize_resources('audios'),
    })
    return data


# ---------------------------------------------------------------------------
# Article endpoints
# ---------------------------------------------------------------------------

@require_GET
def article_list(request: HttpRequest):
    """
    Return a paginated list of published articles.

    Query parameters:
        category    — Filter by one or more category UUIDs, comma-separated (optional).
        page        — Page number, 1-based (default: 1).
        page_size   — Items per page (default: 10, max: 100).
        order       — Sort field: published_at, -published_at, created_at,
                      -created_at, sort_order, -sort_order (default: -published_at).
        top         — If "1", return only is_top articles.
        recommended — If "1", return only is_recommended articles.
    """
    category_param = request.GET.get('category', '')
    category_uuids = []
    if category_param:
        try:
            category_uuids = [UUID(c.strip()) for c in category_param.split(',') if c.strip()]
        except ValueError:
            return error(ErrorCode.BAD_REQUEST, _('Invalid category UUID.'))

    try:
        page_num = max(1, int(request.GET.get('page', 1)))
        page_size = min(100, max(1, int(request.GET.get('page_size', 10))))
    except ValueError:
        return error(ErrorCode.BAD_REQUEST, _('page and page_size must be integers.'))

    order = request.GET.get('order', '-published_at')
    if order not in ALLOWED_ORDER_FIELDS:
        return error(ErrorCode.BAD_REQUEST, _('Invalid order field.'))

    top_only = request.GET.get('top') == '1'
    recommended_only = request.GET.get('recommended') == '1'

    page = ArticleFrontendService.get_article_list(
        category=category_uuids,
        page_number=page_num,
        page_size=page_size,
        order_by=[order],
        top_only=top_only,
        recommended_only=recommended_only,
    )

    return success(data={
        'items': [_serialize_article_summary(a) for a in page],
        'page': page.number,
        'page_size': page_size,
        'total_pages': page.paginator.num_pages,
        'total_count': page.paginator.count,
    })


@require_GET
def article_detail(request: HttpRequest, uuid: UUID):
    """Return a single published article by UUID."""
    article = ArticleFrontendService.get_article_by_uuid(uuid, ArticleType.ARTICLE)
    if article is None:
        return error(ErrorCode.NOT_FOUND, _('Article not found.'))
    return success(data=_serialize_article_detail(article))


@require_GET
def page_detail(request: HttpRequest, uuid: UUID):
    """
    Return a single published page by UUID.
    Pages are articles with type=PAGE.
    """
    page = ArticleFrontendService.get_article_by_uuid(uuid, ArticleType.PAGE)
    if page is None:
        return error(ErrorCode.NOT_FOUND, _('Page not found.'))
    return success(data=_serialize_article_detail(page))


# ---------------------------------------------------------------------------
# Category endpoints
# ---------------------------------------------------------------------------

@require_GET
def category_list(request: HttpRequest):
    """Return all active categories ordered by sort_order."""
    categories = CategoryFrontendService.get_category_list()
    return success(data={
        'items': [_serialize_category(c) for c in categories],
    })


@require_GET
def category_detail(request: HttpRequest, uuid: UUID):
    """Return a single active category by UUID."""
    category = CategoryFrontendService.get_category_by_uuid(uuid)
    if category is None:
        return error(ErrorCode.NOT_FOUND, _('Category not found.'))
    return success(data=_serialize_category(category))

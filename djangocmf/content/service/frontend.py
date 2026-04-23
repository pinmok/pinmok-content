#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
frontend module

Description:
  Frontend content service for the content app.

  Provides read-only, published-only queries for frontend views and
  template tags. All methods are language-aware via get_language().

  This module is intentionally separate from the admin-oriented services
  (article.py, category.py) which handle workflow and tree operations.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-04-10
"""
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet, Prefetch
from django.utils.translation import get_language

from djangocmf.content.enums import ArticleStatus, ArticleType
from djangocmf.content.models import Article, ArticleTranslation, Category


# ---------------------------------------------------------------------------
# Article queries
# ---------------------------------------------------------------------------

class ArticleFrontendService:
    """
    Read-only article queries for frontend views and template tags.
    All results are restricted to published articles.
    """

    @classmethod
    def _translation_prefetch(cls, defer_content: bool = False) -> Prefetch:
        """
        Build a Prefetch object for article translations filtered to the current language.

        Args:
            defer_content: If True, defer the content field to reduce data transfer.
                           Use this for list views where article body is not needed.
        """
        lang = get_language()
        qs = ArticleTranslation.objects.filter(language_code=lang)
        if defer_content:
            qs = qs.defer('content')
        return Prefetch('translations', queryset=qs, to_attr='_current_translations')

    @classmethod
    def _base_qs(cls) -> QuerySet:
        """
        Base queryset for detail views: published articles with full translations.
        Includes content field. Use for single article/page retrieval.
        """
        return (
            Article.objects
            .filter(status=ArticleStatus.PUBLISHED)
            .prefetch_related(cls._translation_prefetch())
        )

    @classmethod
    def get_article_by_uuid(cls, uuid) -> Article | None:
        """
        Return a single published article by UUID, or None if not found.
        Prefetches translations for the current language.
        """
        try:
            return (
                cls._base_qs()
                .filter(uuid=uuid)
                .exclude(type=ArticleType.PAGE)
                .get()
            )
        except Article.DoesNotExist:
            return None

    @classmethod
    def get_page_by_uuid(cls, uuid) -> Article | None:
        """
        Return a single published page by UUID, or None if not found.
        Pages are articles with type=PAGE.
        Clean URLs are handled by the URL alias system, not slugs.
        """
        try:
            return (
                cls._base_qs()
                .filter(uuid=uuid, type=ArticleType.PAGE)
                .get()
            )
        except Article.DoesNotExist:
            return None

    @classmethod
    def get_article_list(
            cls,
            *,
            category_uuids: list | None = None,
            page_number: int = 1,
            page_size: int = 10,
            top_only: bool = False,
            recommended_only: bool = False,
            order_by: list[str] = None,
    ) -> Page:
        """
        Return a paginated list of published articles.
        Defers translation content field since list views do not render article body.

        Args:
            category_uuids:   Filter by one or more category UUIDs (OR logic).
                              Pass None or empty list to skip category filtering.
            page_number:      1-based page index.
            page_size:        Number of items per page.
            top_only:         If True, return only is_top articles.
            recommended_only: If True, return only is_recommended articles.
            order_by:         Order articles by this field.

        Returns:
            A Django Page object. Access .object_list for the current page's
            articles, and use page.paginator.num_pages etc. for pagination info.
        """
        qs = (
            Article.objects
            .filter(status=ArticleStatus.PUBLISHED, type=ArticleType.ARTICLE)
            .prefetch_related(cls._translation_prefetch(defer_content=True))
        )

        if category_uuids:
            qs = qs.filter(categories__uuid__in=category_uuids).distinct()

        if top_only:
            qs = qs.filter(is_top=True)

        if recommended_only:
            qs = qs.filter(is_recommended=True)

        order_by = order_by or ['-published_at']
        qs = qs.order_by(*order_by)

        paginator = Paginator(qs, page_size)
        return paginator.get_page(page_number)

    @classmethod
    def get_page_list(cls) -> QuerySet:
        """
        Return all published pages, ordered by sort_order.
        Intended for navigation menus and footer links.
        """
        return (
            cls._base_qs()
            .filter(type=ArticleType.PAGE)
            .order_by('sort_order', 'published_at')
        )


# ---------------------------------------------------------------------------
# Category queries
# ---------------------------------------------------------------------------

class CategoryFrontendService:
    """
    Read-only category queries for frontend views and template tags.
    All results are restricted to active categories.
    """

    @classmethod
    def _base_qs(cls) -> QuerySet:
        """Base queryset: active categories only."""
        return Category.objects.filter(is_active=True)

    @classmethod
    def get_category_by_uuid(cls, uuid) -> Category | None:
        """Return a single active category by UUID, or None if not found."""
        try:
            return cls._base_qs().get(uuid=uuid)
        except Category.DoesNotExist:
            return None

    @classmethod
    def get_root_categories(cls) -> QuerySet:
        """Return all active top-level categories (parent=None), ordered."""
        return (
            cls._base_qs()
            .filter(parent__isnull=True)
            .order_by('sort_order', 'id')
        )

    @classmethod
    def get_children(cls, category: Category) -> QuerySet:
        """Return active direct children of the given category, ordered."""
        return (
            cls._base_qs()
            .filter(parent=category)
            .order_by('sort_order', 'id')
        )

    @classmethod
    def get_category_list(cls) -> QuerySet:
        """
        Return all active categories ordered for flat display.
        Suitable for navigation menus and category listing pages.
        """
        return cls._base_qs().order_by('sort_order', 'id')

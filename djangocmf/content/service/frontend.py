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
    def _base_qs(cls) -> QuerySet:
        """Base queryset: published articles only, with translations prefetched."""
        lang = get_language()
        return (
            Article.objects
            .filter(status=ArticleStatus.PUBLISHED)
            .prefetch_related(
                Prefetch(
                    'translations',
                    queryset=ArticleTranslation.objects.filter(language_code=lang),
                    to_attr='_current_translations',
                )
            )
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
    ) -> Page:
        """
        Return a paginated list of published articles.

        Args:
            category_uuids: Filter by one or more category UUIDs (OR logic).
                            Pass None or empty list to skip category filtering.
            page_number:    1-based page index.
            page_size:      Number of items per page.
            top_only:       If True, return only is_top articles.
            recommended_only: If True, return only is_recommended articles.

        Returns:
            A Django Page object. Access .object_list for the current page's
            articles, and use page.paginator.num_pages etc. for pagination info.
        """
        qs = cls._base_qs().exclude(type=ArticleType.PAGE)

        if category_uuids:
            qs = qs.filter(categories__uuid__in=category_uuids).distinct()

        if top_only:
            qs = qs.filter(is_top=True)

        if recommended_only:
            qs = qs.filter(is_recommended=True)

        qs = qs.order_by('-is_top', '-published_at')

        paginator = Paginator(qs, page_size)
        return paginator.get_page(page_number)

    @classmethod
    def get_top_articles(cls, limit: int = 5) -> QuerySet:
        """
        Return the most recent top-pinned published articles.
        Not paginated; intended for sidebar/featured slots.
        """
        return (
            cls._base_qs()
            .exclude(type=ArticleType.PAGE)
            .filter(is_top=True)
            .order_by('-published_at')[:limit]
        )

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

    @classmethod
    def get_recommended_articles(cls, limit: int = 10) -> QuerySet:
        """
        Return the most recent recommended published articles.
        Not paginated; intended for homepage recommendation blocks.
        """
        return (
            cls._base_qs()
            .exclude(type=ArticleType.PAGE)
            .filter(is_recommended=True)
            .order_by('-published_at')[:limit]
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

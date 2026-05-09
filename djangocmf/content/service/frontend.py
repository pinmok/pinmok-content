#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
frontend module

Description:
  Frontend content service for the content app.

  Provides read-only, published-only queries for frontend views and
  template tags. All methods are language-aware via the translation layer.

  This module is intentionally separate from the admin-oriented services
  (article.py, category.py) which handle workflow and tree operations.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-04-10
"""
from uuid import UUID

from django.core.paginator import Paginator, Page
from django.db.models import QuerySet

from djangocmf.content.enums import ArticleStatus, ArticleType, Usage
from djangocmf.content.models import Article, Category


# ---------------------------------------------------------------------------
# Article queries
# ---------------------------------------------------------------------------

class ArticleFrontendService:
    """
    Read-only article queries for frontend views and template tags.
    All results are restricted to published articles.
    Translation is handled transparently via TranslatableModel.
    """

    @classmethod
    def _base_qs(cls) -> QuerySet:
        """
        Base queryset for detail views: published articles with translations prefetched.
        Use for single article/page retrieval.
        """
        return Article.with_translations(
            Article.objects.filter(status=ArticleStatus.PUBLISHED)
        )

    @classmethod
    def get_article_by_uuid(cls, uuid: UUID) -> Article | None:
        """
        Return a single published article by UUID, or None if not found.
        Translations are prefetched for the current language.
        """
        try:
            art = (
                cls._base_qs()
                .prefetch_related('article_resources__resource')
                .filter(uuid=uuid)
                .get()
            )
            all_resources = list(art.article_resources.all())
            art.gallery = [r for r in all_resources if r.usage == Usage.GALLERY]
            art.attachments = [r for r in all_resources if r.usage == Usage.ATTACHMENT]
            art.videos = [r for r in all_resources if r.usage == Usage.VIDEO]
            art.audios = [r for r in all_resources if r.usage == Usage.AUDIO]
            return art
        except Article.DoesNotExist:
            return None

    @classmethod
    def get_article_list(
            cls,
            *,
            category: list[UUID],
            page_number: int = 1,
            page_size: int = 10,
            limit: int | None = None,
            top_only: bool = False,
            recommended_only: bool = False,
            order_by: list[str] | None = None,
    ) -> Page | list:
        """
        Return a paginated list or a plain list of published articles.

        Args:
            category:         Filter by one or more category UUIDs (OR logic).
                              Pass None or empty list to skip category filtering.
            page_number:      1-based page index. Ignored when limit is set.
            page_size:        Number of items per page. Ignored when limit is set.
            limit:            If set, disables pagination and returns a plain list of at most N articles.
            top_only:         If True, return only is_top articles.
            recommended_only: If True, return only is_recommended articles.
            order_by:         List of order fields e.g. ['-published_at']. Defaults to ['-published_at'].

        Returns:
            A plain list when limit is set, otherwise a Django Page object.
        """
        qs = Article.with_translations(
            Article.objects
            .filter(status=ArticleStatus.PUBLISHED, type=ArticleType.ARTICLE)
        )

        # Optionally filter by one or more category UUIDs (OR logic)
        qs = qs.filter(
            categories__uuid__in=[u for u in category if u]
        ).distinct()

        # Optionally filter to top-pinned articles only
        if top_only:
            qs = qs.filter(is_top=True)

        # Optionally filter to recommended articles only
        if recommended_only:
            qs = qs.filter(is_recommended=True)

        # Apply ordering, default to newest published first
        order_by = order_by or ['-published_at']
        qs = qs.order_by(*order_by)

        if limit is not None:
            return list(qs[:limit])

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
    Translation is handled transparently via TranslatableModel.
    """

    @classmethod
    def _base_qs(cls) -> QuerySet:
        """Base queryset: active categories with translations prefetched."""
        return Category.with_translations(
            Category.objects.filter(is_active=True)
        )

    @classmethod
    def get_category_by_uuid(cls, uuid: UUID) -> Category | None:
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

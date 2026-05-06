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
from uuid import UUID

from django.core.paginator import Paginator, Page
from django.db.models import QuerySet, Prefetch
from django.utils.translation import get_language

from djangocmf.content.enums import ArticleStatus, ArticleType
from djangocmf.content.models import Article, ArticleTranslation, Category

_TRANSLATION_PREFETCH_NAME = 'current_translations'


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
        return Prefetch('translations', queryset=qs, to_attr=_TRANSLATION_PREFETCH_NAME)

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
    def _attach_translation(cls, article: Article):
        """
        Attach a `translation` attribute and proxy common fields directly onto
        the article instance so templates can use {{ article.title }} uniformly.
        """
        cached = getattr(article, _TRANSLATION_PREFETCH_NAME, None)
        if cached is not None:
            translation = cached[0] if isinstance(cached, list) and cached else None
        else:
            translation = article.get_translation()

        if translation:
            # _meta is a Django convention, safe to access directly
            for field in translation._meta.fields:  # noqa
                if field.name not in ('id', 'article_id'):
                    setattr(article, field.name, getattr(translation, field.name))
        return article

    @classmethod
    def get_article_by_uuid(cls, uuid: UUID) -> Article | None:
        """
        Return a single published article by UUID, or None if not found.
        Prefetches translations for the current language.
        """
        try:
            art = cls._base_qs().filter(uuid=uuid).get()
            cls._attach_translation(art)
            return art
        except Article.DoesNotExist:
            return None

    @classmethod
    def get_article_list(
            cls,
            *,
            category: str | UUID | list[str],
            page_number: int = 1,
            page_size: int = 10,
            limit: int | None = None,
            top_only: bool = False,
            recommended_only: bool = False,
            order_by: list[str] | None = None,
    ) -> Page | list:
        """
        Return a paginated list or a plain list of published articles.
        Defers translation content field since list views do not render article body.

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
        category_uuids = [category] if not isinstance(category, list) else category

        qs = (
            Article.objects
            # Only return published articles, exclude pages and other types
            .filter(status=ArticleStatus.PUBLISHED, type=ArticleType.ARTICLE)
            # Prefetch translations for the current language, defer content field for performance
            .prefetch_related(cls._translation_prefetch(defer_content=True))
        )

        # Optionally filter by one or more category UUIDs (OR logic)
        qs = qs.filter(categories__uuid__in=category_uuids).distinct()

        # Optionally filter to top-pinned articles only
        if top_only:
            qs = qs.filter(is_top=True)

        # Optionally filter to recommended articles only
        if recommended_only:
            qs = qs.filter(is_recommended=True)

        # Apply ordering, default to newest published first
        order_by: list[str] = order_by or ['-published_at']
        qs = qs.order_by(*order_by)

        if limit is not None:
            # limit mode: skip pagination, return a plain list of at most N articles
            articles = list(qs[:limit])
        else:
            # pagination mode: return a Django Page object for the requested page
            paginator = Paginator(qs, page_size)
            articles = paginator.get_page(page_number)

        # Proxy translation fields (title, summary, etc.) directly onto each article instance
        # so templates can use {{ article.title }} instead of {{ article.translation.title }}
        for art in articles:
            cls._attach_translation(art)

        return articles

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

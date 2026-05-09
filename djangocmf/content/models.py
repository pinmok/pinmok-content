#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content.models module

Description:
  Models for Content of DjangoCMF
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-01-17
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from djangocmf.cmfadmin.models import Resource
from djangocmf.content.enums import ArticleStatus, ArticleType, Usage, TemplateAction
from djangocmf.core.constants import DEFAULT_SORT_ORDER, TRANSLATION_RELATED_NAME
from djangocmf.core.translatable import TranslatableModel, TranslationModel


class Category(TranslatableModel):
    """ Article category """
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('parent category'),
        related_name='children',
    )
    uuid = models.UUIDField(
        'UUID',
        max_length=32,
        unique=True,
        default=uuid.uuid4
    )
    cover = models.ImageField(
        _('cover image'),
        null=True,
        blank=True,
    )
    template = models.CharField(
        _('template'),
        max_length=255,
        blank=True,
        default=TemplateAction.LIST
    )
    is_active = models.BooleanField(
        _('is active'),
        default=True
    )
    sort_order = models.PositiveIntegerField(
        _('sort order'),
        default=DEFAULT_SORT_ORDER
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['sort_order', 'id']


class CategoryTranslation(TranslationModel):
    """ Language-specific translation for a category. """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name=TRANSLATION_RELATED_NAME,
        verbose_name=_('category'),
    )
    name = models.CharField(
        _('category name'),
        max_length=255,
    )
    description = models.CharField(
        _('description'),
        max_length=200,
        blank=True,
        default='',
    )

    class Meta:
        verbose_name = _('category translation')
        verbose_name_plural = _('category translations')
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'language'],
                name='uniq_category_language'
            )
        ]

    def get_display_text(self):
        return self.name


class Article(TranslatableModel):
    """
    Article master record. Language-independent fields only.
    Translatable content is stored in ArticleTranslation.
    """
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='articles',
        verbose_name=_('categories')
    )
    uuid = models.UUIDField(
        'UUID',
        max_length=32,
        unique=True,
        default=uuid.uuid4
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=ArticleType.choices,  # noqa
        default=ArticleType.ARTICLE
    )
    template = models.CharField(
        _('template'),
        max_length=255,
        blank=True,
        default=TemplateAction.ARTICLE
    )
    cover = models.ImageField(
        _('cover image'),
        null=True,
        blank=True,
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=ArticleStatus.choices,  # noqa
        default=ArticleStatus.DRAFT
    )
    sort_order = models.PositiveIntegerField(
        _('sort order'),
        default=DEFAULT_SORT_ORDER
    )
    extra = models.JSONField(
        _('extra'),
        default=dict,
        blank=True
    )
    is_top = models.BooleanField(
        _('is top'),
        default=False
    )
    is_recommended = models.BooleanField(
        _('recommended'),
        default=False
    )
    published_at = models.DateTimeField(
        _('published at'),
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['-created_at']
        permissions = [
            ('write_article', 'Can write article'),
            ('publish_article', 'Can publish article'),
        ]


class ArticleTranslation(TranslationModel):
    """
    Language-specific content for an Article.
    One row per (article, language_code) combination.
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name=TRANSLATION_RELATED_NAME,
        verbose_name=_('article')
    )
    title = models.CharField(
        _('title'),
        max_length=255,
        default=''
    )
    subtitle = models.CharField(
        _('subtitle'),
        max_length=255,
        blank=True,
        default=''
    )
    summary = models.TextField(
        _('summary'),
        blank=True,
        default=''
    )
    content = models.TextField(
        _('content'),
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = _('article translation')
        verbose_name_plural = _('article translations')
        constraints = [
            models.UniqueConstraint(
                fields=['article', 'language'],
                name='uniq_article_language'
            )
        ]

    def get_display_text(self):
        return self.title


class Page(Article):
    """
    Proxy model for page-type articles.
    Shares the same database table as Article, filtered by type=PAGE.
    """

    class Meta:
        proxy = True
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def save(self, *args, **kwargs):
        # Always enforce type=PAGE for this proxy
        self.type = ArticleType.PAGE
        super().save(*args, **kwargs)


class ArticleResource(models.Model):
    """
    Intermediate table linking Article master records to Resources.
    Shared across all language versions of the same article.
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='article_resources',
        verbose_name=_('article')
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='article_resources',
        verbose_name=_('resource')
    )
    usage = models.CharField(
        _('usage'),
        max_length=20,
        choices=Usage.choices  # noqa
    )
    alt = models.CharField(
        _('alternative text'),
        max_length=255,
        blank=True,
    )
    sort_order = models.PositiveIntegerField(
        _('sort order'),
        default=DEFAULT_SORT_ORDER
    )

    class Meta:
        verbose_name = _('article resource')
        verbose_name_plural = _('article resources')
        unique_together = [('article', 'resource', 'usage')]
        ordering = ['sort_order']

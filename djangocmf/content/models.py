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

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from djangocmf.cmfadmin.models import Resource
from djangocmf.content.enums import ArticleStatus, ArticleType, Usage
from djangocmf.core.constants import DEFAULT_SORT_ORDER
from djangocmf.core.utils.helper import get_translated_name


def generate_uuid_hex():
    """
    Django migration cannot serialize lambda functions as default values.
    A named function is required so the migration writer can reference it by import path.
    """
    return uuid.uuid4().hex


class Category(models.Model):
    """ Article category """
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_('parent category'),
        related_name='children',
    )
    template = models.CharField(
        _('template'),
        max_length=255,
        blank=True,
        default=''
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

    def __str__(self):
        return get_translated_name(self)


class CategoryTranslation(models.Model):
    """
    Translated fields for Category.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_('category')
    )
    language = models.CharField(
        _('language'),
        max_length=10,
        choices=settings.LANGUAGES,
    )
    name = models.CharField(
        _('category name'),
        max_length=255
    )
    description = models.CharField(
        _('description'),
        max_length=200,
        blank=True,
        default=''
    )
    meta_title = models.CharField(
        _('meta title'),
        max_length=255,
        blank=True,
        default=''
    )
    meta_keywords = models.CharField(
        _('meta keywords'),
        max_length=255,
        blank=True,
        default=''
    )
    meta_description = models.CharField(
        _('meta description'),
        max_length=160,
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = _('category translation')
        verbose_name_plural = _('category translations')
        unique_together = [('category', 'language')]

    def __str__(self):
        return f"{_('category')}: {self.name}"


class Tag(models.Model):
    """
    Article tag, flat structure.
    """
    is_active = models.BooleanField(
        _('is active'),
        default=True
    )
    sort_order = models.PositiveIntegerField(
        _('sort order'),
        default=DEFAULT_SORT_ORDER
    )

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['sort_order']

    def __str__(self):
        return get_translated_name(self)


class TagTranslation(models.Model):
    """
    Translated fields for Tag.
    """
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_('tag')
    )
    language = models.CharField(
        _('language'),
        max_length=10,
        choices=settings.LANGUAGES,
    )
    name = models.CharField(
        _('name'),
        max_length=255
    )

    class Meta:
        verbose_name = _('tag translation')
        verbose_name_plural = _('tag translations')
        unique_together = [('tag', 'language')]

    def __str__(self):
        return f"{_('name')}: {self.name}"


class Article(models.Model):
    categories = models.ManyToManyField(
        Category,
        blank=True,
        related_name='articles',
        verbose_name=_('categories')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='articles',
        verbose_name=_('tags')
    )
    article_uuid = models.CharField(
        _('UUID'),
        max_length=32,
        unique=True,
        default=generate_uuid_hex  # fix: pass function reference
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
        default=''
    )
    translation_group = models.CharField(
        _('translation group'),
        max_length=32,
        db_index=True,
        default=generate_uuid_hex
    )
    language_code = models.CharField(
        _('language code'),
        max_length=10,
        choices=settings.LANGUAGES
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
    # --- merged from ArticleTranslation ---
    title = models.CharField(
        _('title'),
        max_length=255,
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
    meta_title = models.CharField(
        _('meta title'),
        max_length=255,
        blank=True,
        default=''
    )
    meta_description = models.CharField(
        _('meta description'),
        max_length=500,
        blank=True,
        default=''
    )
    meta_keywords = models.CharField(
        _('meta keywords'),
        max_length=255,
        blank=True,
        default=''
    )
    extra = models.JSONField(
        _('extra'),
        default=dict,
        blank=True
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

    def __str__(self):
        return self.title or f'Article({self.article_uuid})'


class ArticleResource(models.Model):
    """
    Intermediate table for Article and Resource.
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
        _('alt'),
        max_length=255,
        blank=True,
        default=''
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

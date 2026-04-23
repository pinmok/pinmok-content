#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enums module

Description:

Author:
  惠达浪 <crazys@126.com>
Created:
  2026/01/21
"""
from enum import StrEnum

from django.db import models
from django.utils.translation import gettext_lazy as _


class ArticleStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    PENDING = 'pending', _('Pending')
    RETURNED = 'returned', _('Returned')
    PUBLISHED = 'published', _('Published')
    DELETED = 'deleted', _('Deleted')

    @property
    def color(self) -> str:
        colors = {
            self.DRAFT: 'success',
            self.PENDING: 'warning',
            self.RETURNED: 'danger',
            self.PUBLISHED: 'primary',
            self.DELETED: 'dark'
        }
        return colors.get(self, 'secondary')


class ArticleSubmitAction(models.TextChoices):
    PENDING = '_submit_pending', _('Submit for review')
    PUBLISH = '_submit_publish', _('Publish')
    REJECT = '_submit_reject', _('Return')
    RETRACT = '_submit_retract', _('Retract')
    DELETE = '_submit_delete', _('Delete')

    @property
    def target_status(self) -> ArticleStatus:
        return {
            self.PENDING: ArticleStatus.PENDING,
            self.PUBLISH: ArticleStatus.PUBLISHED,
            self.REJECT: ArticleStatus.RETURNED,
            self.RETRACT: ArticleStatus.RETURNED,
            self.DELETE: ArticleStatus.DELETED,
        }[self]


class ArticleType(models.TextChoices):
    ARTICLE = 'article', _('Article')
    PAGE = 'page', _('Page')


class Usage(models.TextChoices):
    GALLERY = 'gallery', _('Gallery')
    ATTACHMENT = 'attachment', _('Attachment')
    VIDEO = 'video', _('Video')
    AUDIO = 'audio', _('Audio')


class TemplateAction(StrEnum):
    INDEX = 'index'
    LIST = 'list'
    ARTICLE = 'article'
    PAGE = 'page'

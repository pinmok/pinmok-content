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
from django.db import models
from django.utils.translation import gettext_lazy as _


class ArticleStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    PENDING = 'pending', _('Pending')
    RETURNED = 'returned', _('Returned')
    PUBLISHED = 'published', _('Published')
    DELETED = 'deleted', _('Deleted')


class ArticleType(models.TextChoices):
    ARTICLE = 'article', _('Article')
    PAGE = 'page', _('Page')


class Usage(models.TextChoices):
    GALLERY = 'gallery', _('Gallery')
    ATTACHMENT = 'attachment', _('Attachment')
    VIDEO = 'video', _('Video')
    AUDIO = 'audio', _('Audio')

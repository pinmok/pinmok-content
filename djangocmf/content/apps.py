#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content.apps module

Description:
  apps module of DjangoCMF content
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-01-17
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContentConfig(AppConfig):
    name = 'djangocmf.content'
    verbose_name = _('Content Management')

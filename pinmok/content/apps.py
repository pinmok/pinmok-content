#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content.apps module

Description:
  apps module of Pinmok content
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-01-17
"""

from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = 'pinmok.content'
    verbose_name = 'Pinmok Content'
    label = name.rpartition('.')[2]

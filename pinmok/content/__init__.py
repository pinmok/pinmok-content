#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
__init__.py

Description:
  A modular Django app providing content management features for Pinmok.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/1/17
"""

from django.utils.version import get_version

VERSION = (1, 0, 0, 'final', 0)
__version__ = get_version(VERSION)

__author__ = "惠达浪"
__author_email = "crazys@126.com"
__title__ = "Pinmok Content"
__license__ = "MIT"
__description__ = "A modular Django app providing content management features for Pinmok."

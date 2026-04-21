#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
datasource module

Description:
  
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/4/20
"""
from django.utils.translation import gettext_lazy as _

from djangocmf.cmfadmin.datasource import datasource
from djangocmf.cmfadmin.widgets import CMFSelect
from djangocmf.content.service.article import ArticleService
from djangocmf.content.service.category import CategoryService


@datasource.register('category')
class CategoryDataSource(CMFSelect):
    def __init__(self, attrs=None):
        choices = [('', _('Select Category'))] + [
            (node.uuid, label)
            for node, label in CategoryService.get_items()
        ]
        super().__init__(attrs=attrs, choices=choices)


@datasource.register('page')
class PageDataSource(CMFSelect):
    def __init__(self, attrs=None):
        choices = [('', _('Select Page'))] + [
            (r['uuid'], r['title'])
            for r in ArticleService.get_pages()
        ]
        super().__init__(attrs=attrs, choices=choices)

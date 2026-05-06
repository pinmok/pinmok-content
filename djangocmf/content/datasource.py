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
from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

from djangocmf.cmfadmin.datasource import datasource
from djangocmf.cmfadmin.widgets import CMFSelect
from djangocmf.content.service.article import ArticleService
from djangocmf.content.service.category import CategoryService


@datasource.register('category')
class CategoryDataSource(CMFSelect):
    def __init__(self, attrs=None, multiple=False):
        choices = [(node.uuid, label) for node, label in CategoryService.get_items()]
        super().__init__(attrs=attrs, choices=choices)
        self.allow_multiple_selected = multiple

    def value_from_datadict(self, data, files, name):
        if self.allow_multiple_selected:
            if isinstance(data, QueryDict):
                return data.getlist(name)
            return data.get(name)
        return super().value_from_datadict(data, files, name)

    def value_omitted_from_data(self, data, files, name):
        if self.allow_multiple_selected:
            return False
        return super().value_omitted_from_data(data, files, name)


@datasource.register('page')
class PageDataSource(CMFSelect):
    def __init__(self, attrs=None):
        choices = [('', _('Select Page'))] + [
            (r['uuid'], r['title'])
            for r in ArticleService.get_pages()
        ]
        super().__init__(attrs=attrs, choices=choices)

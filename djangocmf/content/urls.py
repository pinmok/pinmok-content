#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
urls module

Description:
  URL configuration for the content app.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/01/19
"""

from django.urls import path

from djangocmf.content import views
from djangocmf.content.enums import TemplateAction

urlpatterns = [
    path('', views.index_view, name=TemplateAction.INDEX),
    path('list/<uuid:uuid>/', views.category_list_view, name=TemplateAction.LIST),
    path('article/<uuid:uuid>/', views.article_detail_view, name=TemplateAction.ARTICLE),
    path('page/<uuid:uuid>/', views.page_detail_view, name=TemplateAction.PAGE),
]

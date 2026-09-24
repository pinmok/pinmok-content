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

from django.urls import path, include

from pinmok.content import api, views
from pinmok.content.enums import TemplateAction

api_urlpatterns = [
    path('list/', api.article_list),
    path('article/<uuid:uuid>/', api.article_detail),
    path('page/<uuid:uuid>/', api.page_detail),
    path('categories/', api.category_list),
    path('category/<uuid:uuid>/', api.category_detail),
]

urlpatterns = [
    path('', views.index_view, name=TemplateAction.INDEX),
    path('list/<uuid:uuid>/', views.articles_list_view, name=TemplateAction.LIST),
    path('article/<uuid:uuid>/', views.article_detail_view, name=TemplateAction.ARTICLE),
    path('page/<uuid:uuid>/', views.page_detail_view, name=TemplateAction.PAGE),
    path('api/', include(api_urlpatterns)),
]

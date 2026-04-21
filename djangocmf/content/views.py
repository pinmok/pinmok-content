#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
views module

Description:
  Frontend views for the content app.

  Each view is intentionally thin: fetch data via service, handle 404,
  render template. Business logic lives in services/frontend.py.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-04-10
"""
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext as _

from djangocmf.content.service.frontend import ArticleFrontendService, CategoryFrontendService


def index_view(request):
    """
    Homepage view.
    Renders the index template with no data of its own — content is
    assembled entirely by template tags inside the theme template.
    Users who need a custom homepage should define their own view at
    the empty path before including content.urls.
    """
    # TODO: replace with ThemeService.resolve_template('content.index')
    return render(request, 'themes/default/index.html')


def category_list_view(request, uuid):
    """
    Article list view for a specific category.
    Reads ?page= from query string for pagination.
    """
    category = CategoryFrontendService.get_category_by_uuid(uuid)
    if category is None:
        raise Http404(_('Category not found.'))

    page_number = request.GET.get('page', 1)
    article_page = ArticleFrontendService.get_article_list(
        category_uuids=[uuid],
        page_number=page_number,
    )

    # TODO: replace with ThemeService.resolve_template('content.list')
    return render(request, 'themes/default/list.html', {
        'category': category,
        'article_page': article_page,
    })


def article_detail_view(request, uuid):
    """
    Single article detail view.
    """
    article = ArticleFrontendService.get_article_by_uuid(uuid)
    if article is None:
        raise Http404(_('Article not found.'))

    # TODO: replace with ThemeService.resolve_template('content.article')
    return render(request, 'themes/default/article.html', {
        'article': article,
    })


def page_detail_view(request, uuid):
    """
    Single page detail view.
    Pages are articles with type=PAGE, accessed via UUID.
    Clean URLs are handled by the URL alias system.
    """
    page = ArticleFrontendService.get_page_by_uuid(uuid)
    if page is None:
        raise Http404(_('Page not found.'))

    # TODO: replace with ThemeService.resolve_template('content.page')
    return render(request, 'themes/default/page.html', {
        'page': page,
    })

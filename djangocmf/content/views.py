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
from uuid import UUID

from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext as _

from djangocmf.cmfadmin.service.theme import ThemeService
from djangocmf.content.enums import TemplateAction
from djangocmf.content.service.frontend import ArticleFrontendService, CategoryFrontendService


def _theme_render(request, action: TemplateAction, filename: str, context: dict = None):
    """Resolve template path, inject theme vars, and render."""
    template_path = ThemeService.get_template_path(filename)
    if template_path is None:
        raise Http404(_('No active theme.'))
    ctx = ThemeService.get_vars_context(action)
    if context:
        ctx.update(context)
    return render(request, template_path, ctx)


def index_view(request):
    """
    Homepage view.
    Renders the index template with no data of its own — content is
    assembled entirely by template tags inside the theme template.
    Users who need a custom homepage should define their own view at
    the empty path before including content.urls.
    """
    template = ThemeService.get_template_path(TemplateAction.INDEX)
    if template is None:
        # No active theme or index template not found, fall back to demo
        return render(request, 'content/welcome.html')

    ctx = ThemeService.get_vars_context(TemplateAction.INDEX)
    return render(request, template, ctx)


def category_list_view(request, uuid: UUID):
    """
    Article list view for a specific category.
    Reads ?page= from query string for pagination.
    """
    category = CategoryFrontendService.get_category_by_uuid(uuid)
    if category is None:
        raise Http404(_('Category not found.'))

    page_number = int(request.GET.get('page', 1))
    articles = ArticleFrontendService.get_article_list(
        category_uuids=[uuid],
        page_number=page_number,
    )
    return _theme_render(request, TemplateAction.LIST, category.template, {
        'category': category,
        'article_list': articles,
    })


def article_detail_view(request, uuid):
    """
    Single article detail view.
    """
    article = ArticleFrontendService.get_article_by_uuid(uuid)
    if article is None:
        raise Http404(_('Article not found.'))

    return _theme_render(request, TemplateAction.ARTICLE, article.template, {'article': article})


def page_detail_view(request, uuid):
    """
    Single page detail view.
    Pages are articles with type=PAGE, accessed via UUID.
    Clean URLs are handled by the URL alias system.
    """
    page = ArticleFrontendService.get_page_by_uuid(uuid)
    if page is None:
        raise Http404(_('Page not found.'))
    return _theme_render(request, TemplateAction.PAGE, page.template, {'page': page})
